#!/usr/bin/env python
import logging
import subprocess
import tempfile

from mptcpanalyzer.core import build_csv_header_from_list_of_fields 
# from . import fields_dict
# , get_basename

log = logging.getLogger(__name__)


class TsharkExporter:
    """
    TODO tshark.py devrait plutot accepter des streams

    """

    input_pcap = ""
    tshark_bin = None
    tcp_relative_seq = True
    options = {
        "tcp.relative_sequence_numbers": True if tcp_relative_seq else False,
        # "tcp.relative_sequence_numbers": 
        # Disable DSS checks which consume quite a lot
        # "tcp.analyze_mptcp_seq": False,
        # "tcp.analyze_mptcp": True,
        # "tcp.analyze_mptcp_mapping": False,
    }    
    delimiter = '|'
    # fields_to_export = (
    #     "packetid", 
    #     "time",
    #     "mptcpstream", 
    #     "tcpstream", 
    # )

    # TODO should be settable
    # mptcp.stream
    filter = ""

    def __init__(self, tshark_bin="/usr/bin/wireshark"):
        self.tshark_bin = tshark_bin
        # self.fields_to_export = fields_to_export
        pass

    def export_pcap_to_csv(self, input_pcap, output_csv, fields_to_export):
        """
        fields_to_export = dict
        """
        log.info("Converting pcap [{pcap}] to csv [{csv}]".format(
            pcap=input_pcap,
            csv=output_csv)
        )

        # TODO should export everything along with TCP acks
        # TODO should accept a filter mptcp stream etc...
        # ands convert some parts of the filter into an SQL request
        # output = ""
        header = build_csv_header_from_list_of_fields(fields_to_export.keys(), self.delimiter)        

        # output = output if output else ""
        log.info("Writing to file %s" % output_csv)
        # -E occurrence
        with open(output_csv, "w") as f:
            f.write(header)
            # f.write(output.decode())

        return self.tshark_export_fields(
            self.tshark_bin, 
            fields_to_export.values(), 
            input_pcap,
            output_csv,
            self.filter,
            options=self.options,
            # relative_sequence_numbers=self.tcp_relative_seq
        )

    def export_pcap_to_sql(self, input_pcap, output_db, table_name="connections"):
        """
        """

        log.info("Converting pcap [{pcap}] to sqlite database [{db}]".format(
            pcap=input_pcap,
            db=output_db
        ))

        # csv_filename = get_basename(output_db, "csv")
        csv_filename = output_db + ".csv"
        self.export_pcap_to_csv(input_pcap, csv_filename)

        convert_csv_to_sql(csv_filename, output_db, table_name)

    @staticmethod
    def tshark_export_fields(tshark_exe, fields_to_export,
                             inputFilename, outputFilename, 
                             filter=None, 
                             options={},
                             csv_delimiter='|',):
        """
        inputFilename should be pcap filename
        fields should be iterable (tuple, list ...)
        returns outout as a string
        """
        def convert_field_list_into_tshark_str(fields):
            """
            TODO fix if empty
            """
            return ' -e ' + ' -e '.join(fields)
        # fields that tshark should export
        # tcp.seq / tcp.ack / ip.src / frame.number / frame.number / frame.time
        # exhaustive list https://www.wireshark.org/docs/dfref/f/frame.html
        # tcp.options.mptcp.subtype == 2 => DSS (0 => MP-CAPABLE)
        # to filter connection
        filter = '-2 -R "%s"' % (filter) if filter else ''

        def convert_options_into_str(options):
            """
            Expects a dict of wireshark options
            TODO maybe it could use **kwargs instead 
            """
            # relative_sequence_numbers = False
            out = ""
            for option, value in options.items():
                out += ' -o {option}:{value}'.format(option=option, value=value)
            return out

        print(fields_to_export)
        # for some unknown reasons, -Y does not work so I use -2 -R instead
        # quote=d|s|n Set the quote character to use to surround fields.  d uses double-quotes, s
        # single-quotes, n no quotes (the default).
        #  -E quote=n 
        cmd = """{tsharkBinary} {tsharkOptions} {nameResolution} {filterExpression} -r {inputPcap} -T fields {fieldsExpanded} -E separator='{delimiter}' >> {outputFilename}
                 """.format(
            tsharkBinary=tshark_exe,
            tsharkOptions=convert_options_into_str(options),
            nameResolution="-n",
            inputPcap=inputFilename,
            outputCsv=outputFilename,
            fieldsExpanded=convert_field_list_into_tshark_str(fields_to_export),
            filterExpression=filter,
            delimiter=csv_delimiter,
            outputFilename=outputFilename
        )
        print(cmd)

        try:
            # https://docs.python.org/3/library/subprocess.html#subprocess.check_output
            # output = subprocess.Popen(cmd, shell=True) stdout=subprocess.PIPE, 
            proc = subprocess.Popen(cmd, stderr=subprocess.PIPE, shell=True)
            out, stderr = proc.communicate()
            # out = out.decode("UTF-8")
            stderr = stderr.decode("UTF-8") 
            print("stderr=", stderr)
        except subprocess.CalledProcessError as e:
            log.error(e)
            print("ERROR")
            output = " ehllo "
        # os.system(cmd)
        # except CalledProcessError as e:
        # print(output)
        return proc.returncode, stderr


# Ideally I would have liked to rely on some external library like
# querycsv, csvkit etc... but they all seem broken in one way or another
# https://docs.python.org/3.4/library/sqlite3.html
def convert_csv_to_sql(csv_filename, database, table_name):
    # sqlite3
    # 
    # > .separator ","
    # > .import test.csv TEST
    """
    csv_filename
    csv_content should be a string
    Then you can run SQL commands via SQLite Manager (firefox addo 
    """

    log.info("Converting csv to sqlite table {table} into {db}".format(
        table=table_name,
        db=database
    ))
    # db = sqlite.connect(database)
    # csv_filename
    # For the second case, when the table already exists, 
    # every row of the CSV file, including the first row, is assumed to be actual content. If the CSV file contains an initial row of column labels, that row will be read as data and inserted into the table. To avoid this, make sure that table does not previously exist. 
    #
    init_command = (
        "DROP TABLE IF EXISTS {table};\n"
        ".separator {delimiter}\n"
        # ".mode csv\n"
        ".import {csvFile} {table}\n"
    ).format(delimiter="|",
             csvFile=csv_filename,
             table=table_name)

    # initCommand=
    #     "DROP TABLE IF EXISTS {table};\n"
    #     ".separator '{separator}'\n"
    #         ".import {csvFile} {table}\n").format(
    #         separator=",",
    #         csvFile=csv_filename,
    #         table=table_name
    #         )
    # print(initCommand)
    log.info("Creating db %s (if does not exist)" % database)
    with tempfile.NamedTemporaryFile("w+", delete=False) as f:
        # with open(tempInitFilename, "w+") as f:
        f.write(init_command)
        f.flush()

        cmd = "sqlite3 -init {initFilename} {db} ".format(
            initFilename=f.name,
            db=database,
            # init=init_command
        )

        # cmd="sqlite3"
        # tempInitFilename      
        log.info("Running command:\n%s" % cmd)
        # input=init_command.encode(),
        try:

            output = subprocess.check_output(cmd, 
                                             input=".exit".encode(),
                                             shell=True)
        except subprocess.CalledProcessError as e:
            log.error(e)
            output = "Failure" + str(e)

    return output
