from IPython.core.magic import register_cell_magic
import treeppl as treeppl_


@register_cell_magic
def treeppl(line, cell):
    args = line.split(maxsplit=1)
    if not args:
        raise ValueError("you must provide a variable name after %%treeppl")
    ip = get_ipython()
    compile_arguments = treeppl_.CompileArguments()
    if len(args) == 2:
        compile_arguments.parse_opts(args[1])
    ip.user_ns[args[0]] = treeppl_.Model(source=cell, **compile_arguments)


@register_cell_magic
def treeppl_source(line, cell):
    variable_name = line.strip()
    if not variable_name:
        raise ValueError("you must provide a variable name after %%treeppl_source")
    ip = get_ipython()
    ip.user_ns[variable_name] = cell


def load_ipython_extension(ipython):
    ipython.register_magic_function(treeppl, "cell")
    ipython.register_magic_function(treeppl_source, "cell")
