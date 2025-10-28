import pytest
import treeppl
import numpy as np


def test_compilation_error():
    with pytest.raises(treeppl.CompileError):
        with treeppl.Model(
            source="""\
model incorrect() {
  return result;
}
""",
            samples=1,
        ) as model:
            model()


def test_coin():
    nsamples = 100
    with treeppl.Model(filename="examples/coin.tppl", samples=nsamples) as coin:
        res = coin(outcomes=(np.random.random(10) < 0.5).tolist())
        assert isinstance(res, treeppl.InferenceResult)
        assert len(res.samples) == nsamples


def test_matrix_mul():
    np.random.seed(42)
    a = np.random.randint(-5, 6, size=(3, 2))
    b = np.random.randint(-5, 6, size=(2, 4))
    expected = a @ b
    with treeppl.Model(
        source="""\
model function matrix_mul(a: Matrix[Real], b: Matrix[Real]) => Matrix[Real] {
  return a *@ b;
}
""",
        samples=1,
    ) as matrix_mul:
        result = matrix_mul(a=a, b=b).samples[0]
    assert (result == expected).all()


def test_tree_input():
    tree = treeppl.Tree.Node(
        left=treeppl.Tree.Node(
            left=treeppl.Tree.Leaf(age=0.0), right=treeppl.Tree.Leaf(age=0.0), age=0.5
        ),
        right=treeppl.Tree.Leaf(age=0.0),
        age=1.0,
    )
    with treeppl.Model(
        source="""\
function count_leaves(tree: Tree) => Int {
  if tree is Node {
    return count_leaves(tree.left) + count_leaves(tree.right);
  }
  return 1;
}

model function count_tree_leaves(tree: Tree) => Int {
  return count_leaves(tree);
}
""",
        samples=1,
    ) as count_tree_leaves:
        res = count_tree_leaves(tree=tree)
        assert res.samples[0] == 3
