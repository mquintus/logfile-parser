"""
Let's search through some logfiles
"""
import re
import pandas as pd
import plotly.express as px
import logging
import argparse


def createDataframeFromFile(filename, formatting, read_line_limit=1_000):
    df = pd.DataFrame()
    f = open(filename, "r")
    i = 0
    for line in f:
        i += 1
        row = re.match(formatting["regex"], line)
        if row:
            df = pd.concat([df, pd.DataFrame([row.groups()])], ignore_index=True)
        else:
            logging.warning(f"Skipping line {i}: {line[:-1]}")
        if read_line_limit > 0 and i > read_line_limit:
            break
    f.close()
    df.columns = formatting["columns"]
    return df


def parseArguments(cmd_args=None):
    parser = argparse.ArgumentParser(
        prog="Logfile-Parser.py",
        description="Parse log files. Filter by field and value.",
        epilog="Enjoy the program! :)",
    )
    parser.add_argument(
        "-p", "--plot", action="store_true", help="Plot the data with Plotly."
    )
    parser.add_argument(
        "-b", "--basedir", action="store", type=str, default="./", help="Plot the data with Plotly."
    )
    parser.add_argument(
        "-t",
        "--type",
        type=str,
        action="store",
        choices=["access", "error", "apache", "auth"],
        default="access",
    )
    parser.add_argument(
        "-ff",
        "--filter-field",
        type=str,
        action="store",
    )
    parser.add_argument(
        "-fv",
        "--filter-value",
        type=str,
        action="store",
    )
    parser.add_argument(
        "-c",
        "--column",
        type=str,
        action="store",
    )
    parser.add_argument("--read_line_limit", type=int, action="store", default=1_000)
    parser.add_argument(
        "-v", "--verbose", action="count", default=0, help="Verbosity level."
    )
    parser.add_argument(
        "-a", "--all", action="store_true", help="Parse all lines."
    )
    args = parser.parse_args(cmd_args)
    if args and args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
        logging.debug("Verbose output.")
        logging.debug(args)
        logging.debug("")

    return args


def main():
    args = parseArguments()
    parseLogs(args)

'''
    Return a dict with keys
    "regex" and "columns"
'''
def getLogFileFormatting(args):
    formatting_access = {
        # Kudos to https://stackoverflow.com/questions/12544510/parsing-apache-log-files
        "regex": '([(\d\.)]+) ([^\s+]) - \[(.*?)\] "(.*?)" (\d+) (\d+) "(.*?)" "(.*?)"',
        "columns": (
            "ip",
            "user",
            "date",
            "request",
            "status",
            "size",
            "unknown",
            "user agent",
        ),
    }
    formatting_error = {
        "regex": "\[(.*?)\] \[(.*?)\] \[(pid.*?)\] (\[client (.*?):(.*?)\])? (.*)",
        "columns": ("date", "error", "pid", "client", "ip", "port", "message"),
    }
    formatting_auth = {
#        "regex":  "(.{15}) (\w?) (\w*?)\[(\d*)\]: (\w*) user (.*?) .* (?:from)? (.*?) port (\d*) (\w*)",
#        "columns": ("date", "host", "service", "pid", "event", "user", "ip", "port", "method"),
        "regex":  "^(.{15}) (\w*) (\w*)\[(\d*)\]: (.*?)( user \w*)?(?: from )?(\d+\.\d+\.\d+\.\d+)? (port \d+)?",
        "columns": ("date", "host", "service", "pid", "event", "user", "ip", "port"),
    }
    if args.type in ["access"]:
        return formatting_access
    if args.type in ["error"]:
        return formatting_error
    if args.type in ["auth"]:
        return formatting_auth
    return {"regex": "", "columns": ()}


def parseLogs(args):
    df = pd.DataFrame()
    # Parse access.log
    if args.type in ["access", "apache"]:
        print("Parse access.log")
        formatting_access = getLogFileFormatting(args)
        df_access = createDataframeFromFile(args.basedir+"logs/access.log", formatting_access, read_line_limit=args.read_line_limit)
        logging.debug("\n" + df_access.iloc[:20].to_markdown())
        logging.debug("")
        logging.debug("\n" + df_access.value_counts("status").to_markdown() + "\n")
        logging.debug("\n" + df_access.value_counts("ip")[:10].to_markdown() + "\n")
        logging.debug(
            "\n" + df_access.value_counts("request")[:10].to_markdown() + "\n"
        )
        logging.debug(
            "\n" + df_access.value_counts("user agent")[:10].to_markdown() + "\n"
        )
        df = df_access

    # Parse error.log
    if args.type in ["error", "apache"]:
        print("Parse error.log")
        formatting_error = getLogFileFormatting(args)
        df_error = createDataframeFromFile(args.basedir+"logs/error.log", formatting_error, read_line_limit=args.read_line_limit)
        logging.debug("\n" + df_error.iloc[:10].to_markdown())
        logging.debug("")
        logging.debug("\n" + df_error.value_counts("error").to_markdown() + "\n")
        logging.debug("\n" + df_error.value_counts("ip")[:10].to_markdown() + "\n")
        logging.debug("\n" + df_error.value_counts("message")[:10].to_markdown() + "\n")
        logging.debug("")
        df = pd.concat([df, df_error])

    # Parse auth.log
    if args.type in ["auth"]:
        formatting_auth = getLogFileFormatting(args)
        df_auth = createDataframeFromFile(args.basedir+"logs/auth.log", formatting_auth, read_line_limit=args.read_line_limit)
        logging.debug("\n" + df_auth.iloc[:10].to_markdown())
        df = pd.concat([df, df_auth])

    # Filter by field and value
    if args.filter_field and args.filter_value:
        df = df[df[args.filter_field] == args.filter_value]

    # Print the dataframe
    if args.column:
        field_of_interest = args.column
        if args.all:
            print(df.value_counts(field_of_interest).to_markdown())
        else:
            print(df.value_counts(field_of_interest)[:30].to_markdown())
            if len(df.value_counts(field_of_interest)) > 30:
                print("[truncated]")
        #print(df[field_of_interest].unique().to_markdown())
    #else:
    #    print(df.to_markdown())

    if args.plot:
        logging.info("Plotting data with Plotly.")
        px.scatter(df, x="status", y="date", hover_name="request", log_x=True).show()

    # import plotly.express as px
    # df = px.data.gapminder().query("year == 2007")

    # fig = px.scatter(df, x="gdpPercap", y="lifeExp", hover_name="country", log_x=True)
    # fig.show()


if __name__ == "__main__":
    main()
