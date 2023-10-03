from .serialization import Object, constructor


class Tree:
    @constructor("Node")
    class Node(Object):
        def __repr__(self):
            return f"Node(left={self.left!r}, right={self.right!r}, age={self.age})"

    @constructor("Leaf")
    class Leaf(Object):
        def __repr__(self):
            return f"Leaf(age={self.age})"

    @staticmethod
    def load(filename, format="nexus"):
        if format == "phyjson":
            return Tree.load_phyjson(filename)
        return Tree.load_biopython(filename, format)


    @staticmethod
    def load_biopython(filename, format="nexus"):
        from Bio import Phylo

        tree = Phylo.read(filename, format)
        if not tree.is_bifurcating():
            return
        tree_depths = tree.depths()
        max_age = max(tree_depths.values())

        def convert(clade):
            if clade.is_terminal():
                return Tree.Leaf(age=max_age - tree_depths[clade])
            else:
                return Tree.Node(
                    left=convert(clade.clades[0]),
                    right=convert(clade.clades[1]),
                    age=max_age - tree_depths[clade],
                )

        return convert(tree.root)

    @staticmethod
    def load_phyjson(filename):
        import json

        def age(node):
            children = node.get("children")
            if children:
                return max(0.0, node.get("branch_length", 0)) + max(
                    age(children[0]), age(children[1])
                )
            return node["branch_length"]

        def convert(node, age):
            age -= max(0, node.get("branch_length"))
            children = node.get("children")
            if children:
                node = Tree.Node(
                    left=convert(children[0], age),
                    right=convert(children[1], age),
                    age=age,
                )
                return node
            else:
                return Tree.Leaf(age=age)

        phyjson = json.load(open(filename, "r"))
        return convert(phyjson["trees"][0]["root"], age(phyjson["trees"][0]["root"]))
