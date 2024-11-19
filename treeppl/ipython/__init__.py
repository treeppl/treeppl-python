from IPython.core.magic import register_cell_magic
from IPython.display import Javascript, display
import treeppl as treeppl_


@register_cell_magic
def treeppl(line, cell):
    args = line.split()
    if not args:
        raise ValueError("You must provide a variable name after %%treeppl")
    ip = get_ipython()
    kwargs = dict(
        arg.strip().split("=", 1) if "=" in arg else (arg.strip(), True)
        for arg in args[1:]
    )
    ip.user_ns[args[0]] = treeppl_.Model(source=cell, **kwargs)


@register_cell_magic
def treeppl_source(line, cell):
    variable_name = line.strip()
    if not variable_name:
        raise ValueError("You must provide a variable name after %%treeppl_source")
    ip = get_ipython()
    ip.user_ns[variable_name] = cell


def load_ipython_extension(ipython):
    ipython.register_magic_function(treeppl, "cell")
    ipython.register_magic_function(treeppl_source, "cell")
    display(
        Javascript(
            r"""
        require(['notebook/js/codecell'], function(codecell) {
            CodeMirror.defineMode("treeppl", function(config, parserConfig) {
                return {
                    startState: function() {
                        return { def: false };
                    },
                    token: function(stream, state) {
                        if (stream.eatSpace()) {
                            return null;
                        }
                        let def = state.def;
                        state.def = false;
                        if (stream.match('//')) {
                            stream.skipToEnd();
                            return "comment";
                        }
                        if (stream.match('/*')) {
                            stream.skipTo('*\\/');
                            return "comment";
                        }
                        if (stream.match(/\b(type|function)\b/)) {
                            state.def = true;
                            return "keyword"
                        }
                        if (stream.match(/\b(model|let|is|in|to|assume|observe|weight|logWeight|resample|if|else|for|return)\b/)) {
                            return "keyword";
                        }
                        if (stream.match(/\b(true|false)\b/)) {
                            return "atom";
                        }
                        if (stream.match(/~|=|==|!=|<|>|<=|>=|\+@|\+|-\*@|\*\$|\*|\$|\^|\/|\^|\|\|/)) {
                            return "operator";
                        }
                        if (stream.match(/\b([A-Za-z][_A-Za-z0-9]*)\b/)) {
                            return def? "def": "variable";
                        }
                        if (stream.match(/\b[+-]?\d+(\.\d)*([Ee][+-]?\d+)?\b/)) {
                            return "number";
                        }
                        if (stream.match(/"([^"\\]|\\.)*"/)) {
                            return "string";
                        }
                        stream.next();
                        return null;
                    }
                };
            });
            codecell.CodeCell.options_default.highlight_modes['treeppl'] = {
                reg: ['^%%treeppl']
            };
        });
    """
        )
    )
