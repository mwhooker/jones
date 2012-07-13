def export_tree(zk, root):
    out = []
    for path in walk(zk, root):
        spacing = ' ' * 2 * (path.count('/') - 1)
        long_spacing = spacing + (' ' * 2)
        out.append(spacing + path)
        data, stat = zk.get(path)
        if len(data):
            out.append(
                ''.join(long_spacing + line for line in data.splitlines(True))
            )
    return '\n'.join(out)


def walk(zk, path='/'):
    """Yields all paths under `path`."""
    children = zk.get_children(path)
    yield path
    for child in children:
        if path == '/':
            subpath = "/%s" % child
        else:
            subpath = "%s/%s" % (path, child)

        for child in walk(zk, subpath):
            yield child
