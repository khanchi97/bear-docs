import os
import inspect

from coalib.settings.ConfigurationGathering import load_configuration
from coalib.misc.DictUtilities import inverse_dicts
from coalib.collecting.Collectors import (
    collect_all_bears_from_sections, filter_section_bears_by_languages)
from pyprint.NullPrinter import NullPrinter
from coalib.output.printers.LogPrinter import LogPrinter

def get_bears():
    """
    Get a dict of bears with the bear class as key.

    :return:
        A dict with bear classes as key and the list of sections
        as value.
    """
    log_printer = LogPrinter(NullPrinter())
    sections, _ = load_configuration(None, log_printer)
    local_bears, global_bears = collect_all_bears_from_sections(
        sections, log_printer)
    return inverse_dicts(local_bears, global_bears)

if __name__ == "__main__":
    bears = get_bears()
    for bear in bears:
        output = "**" + bear.name + "**\n"
        output += "=" * (4 + len(bear.name)) + "\n\n"
        output += bear.get_metadata().desc + "\n\n"
        output += "Supported Languages:" + "\n-----\n\n"
        output += "\n".join(["* " + x for x in bear.supported_languages])
        output += "\n\n"
        docstring = inspect.getdoc(bear.run)
        if docstring:
            docstring = docstring[docstring.find(":param"):]
            docstring = docstring[:docstring.find("\n\n")]
            docstring = docstring[:docstring.find(":return")]
        if docstring:
            par = {}
            lmax = -1
            rmax = -1
            first = True
            for param in docstring.split(":param"):
                if first:
                    first = False
                    continue
                res = param.split(":")
                if len(res) > 2:
                    res = res[0], ":".join(res[1:])
                elif len(res) < 2:
                    continue
                key, meaning = res
                bold = "\\*" if key.strip() in bear.get_metadata().non_optional_params else ""
                key = " ``" + key.strip() + "``" + bold + " "
                meaning = meaning.strip()
                if lmax < len(key):
                    lmax = len(key)
                par[key] = []
                for line in meaning.split("\n"):
                    par[key].append(line.strip())
                    if len(line.strip()) > rmax:
                        rmax = len(line.strip())
            if lmax < len(" Setting"):
                lmax = len(" Setting")
            if rmax < len("Meaning"):
                rmax = len("Meaning")
            header = False
            for key in par:
                if not header:
                    output += "Settings\n--------\n\n"
                    output += "+" + "-" * (lmax) + "-+-" + "-" * (1 + rmax) + "+\n"
                    output += "| Setting" + " " * (lmax - len(" Setting")) + " |  Meaning" + " " * (rmax - len("Meaning")) + "|\n"
                    output += "+" + "=" * lmax + "=+=" + "=" * (1 + rmax) + "+\n"
                    header = True
                output += "| " + " " * lmax + "| " + " " * (1 + rmax) + "|\n"
                output += "|" + key + " " + " " * (lmax - len(key)) + "| " + par[key][0] + " " * (1 + rmax - len(par[key][0]))
                if len(par[key]) > 1:
                    output += "|\n"
                else:
                    output += "+\n"
                for text in par[key][1:]:
                    output += "|" + " " * (lmax + 1) + "| " + text + " " * (1 + rmax - len(text)) + "|\n"
                output += "| " + " " * lmax + "| " + " " * (1 + rmax) + "|\n"
                output += "+" + "-" * lmax + "-+-" + "-" * (1 + rmax) + "+\n"
            output += "\n\* denotes required param"
        with open("docs/" + bear.name + ".rst", "w") as bear_file:
            bear_file.write(output)
        os.system("git add -A && git commit -m 'Add " + bear.name + "'")