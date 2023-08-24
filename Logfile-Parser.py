"""
Let's search through

"""
import re
import pandas as pd
import plotly.express as px
import logging
import argparse

def createDataframeFromFile(filename, formatting):
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
    f.close()
    df.columns = formatting["columns"]
    return df

def parseArguments():
    parser = argparse.ArgumentParser(
        prog="Logfile-Parser.py",
        description="Parse Apache log files. Filter by field and value.",
        epilog="Enjoy the program! :)",
    )
    parser.add_argument(
        "-p", "--plot", action="store_true", help="Plot the data with Plotly.")
    parser.add_argument(
        "-t",
        "--type",
        type=str,
        action="store",
        choices=["access", "error", "all"],
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
    parser.add_argument(
        "-v", "--verbose", action="count", default=0, help="Verbosity level."
    )
    args = parser.parse_args()
    if args and args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
        logging.debug("Verbose output.")
        logging.debug(args)
        logging.debug("")

    return args


def main():
    args = parseArguments()

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

    df = pd.DataFrame()
    if args.type in ["access", "all"]:
        logging.info("Parse access.log")
        df_access = createDataframeFromFile("logs/access.log", formatting_access)
        logging.debug("\n" + df_access.iloc[:10].to_markdown())
        logging.debug("")
        logging.debug("\n" + df_access.value_counts("status").to_markdown() + "\n")
        logging.debug("\n" + df_access.value_counts("ip")[:10].to_markdown() + "\n")
        logging.debug("\n" + df_access.value_counts("request")[:10].to_markdown() + "\n")
        logging.debug("\n" + df_access.value_counts("user agent")[:10].to_markdown() + "\n")
        df = df_access

    if args.type in ["error", "all"]:
        logging.info("Parse error.log")
        df_error = createDataframeFromFile("logs/error.log", formatting_error)
        logging.debug("\n" + df_error.iloc[:10].to_markdown())
        logging.debug("")
        logging.debug("\n" + df_error.value_counts("error").to_markdown() + "\n")
        logging.debug("\n" + df_error.value_counts("ip")[:10].to_markdown() + "\n")
        logging.debug("\n" + df_error.value_counts("message")[:10].to_markdown() + "\n")
        logging.debug("")
        df = pd.concat([df, df_error])


    if args.filter_field and args.filter_value:
        df = df[df[args.filter_field] == args.filter_value]

    if args.column:
        field_of_interest = args.column
        print(df.value_counts(field_of_interest).to_markdown())
    else:
        print(df.to_markdown())

    if args.plot:
        logging.info("Plotting data with Plotly.")
        px.scatter(df, x="status", y="date", hover_name="request", log_x=True).show()

    # import plotly.express as px
    # df = px.data.gapminder().query("year == 2007")

    # fig = px.scatter(df, x="gdpPercap", y="lifeExp", hover_name="country", log_x=True)
    # fig.show()

if __name__ == "__main__":
    main()