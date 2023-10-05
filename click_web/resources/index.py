from collections import OrderedDict
from typing import Tuple, Union

import click
from flask import render_template

import click_web


def index():
    with click.Context(click_web.click_root_cmd, info_name=click_web.click_root_cmd.name, parent=None) as ctx:
        return render_template('show_tree.html.j2', ctx=ctx, tree=_click_to_tree(ctx, click_web.click_root_cmd))


def _click_to_tree(
    ctx: click.Context,
    node: Union[click.Command, click.MultiCommand],
    name: str | None = None,
    ancestors: list[Tuple[str, click.Command | click.MultiCommand]] | None = None,
):
    """
    Convert a click root command to a tree of dicts and lists
    :return: a json like tree
    """
    if ancestors is None:
        ancestors = []
    if name is None:
        name = node.name

    res_childs = []
    res = OrderedDict()
    res['is_group'] = isinstance(node, click.core.MultiCommand)
    if res['is_group']:
        # a group, recurse for every child
        children = [(child_name, node.get_command(ctx, child_name)) for child_name in node.list_commands(ctx)]
        # Sort so commands comes before groups
        children = sorted(children, key=lambda c: isinstance(c[1], click.core.MultiCommand))
        for child_name, child in children:
            res_childs.append(_click_to_tree(ctx, child, child_name, ancestors[:] + [(name, node), ]))

    res['name'] = name

    # Do not include any preformatted block (\b) for the short help.
    res['short_help'] = node.get_short_help_str().split('\b')[0]
    res['help'] = node.help
    path_parts = ancestors + [(name, node)]
    root = click_web._flask_app.config['APPLICATION_ROOT'].rstrip('/')
    # Join names to build path.
    res['path'] = root + '/' + '/'.join(p[0] for p in path_parts)
    if res_childs:
        res['childs'] = res_childs
    return res
