"""CSC148 Assignment 2: Autocompleter classes

=== CSC148 Fall 2018 ===
Department of Computer Science,
University of Toronto

=== Module Description ===
This file contains the design of a public interface (Autocompleter) and two
implementation of this interface, SimplePrefixTree and CompressedPrefixTree.
You'll complete both of these subclasses over the course of this assignment.

As usual, be sure not to change any parts of the given *public interface* in the
starter code---and this includes the instance attributes, which we will be
testing directly! You may, however, add new private attributes, methods, and
top-level functions to this file.
"""
from __future__ import annotations
from typing import Any, List, Optional, Tuple


################################################################################
# The Autocompleter ADT
################################################################################
class Autocompleter:
    """An abstract class representing the Autocompleter Abstract Data Type.
    """
    def __len__(self) -> int:
        """Return the number of values stored in this Autocompleter."""
        raise NotImplementedError

    def insert(self, value: Any, weight: float, prefix: List) -> None:
        """Insert the given value into this Autocompleter.

        The value is inserted with the given weight, and is associated with
        the prefix sequence <prefix>.

        If the value has already been inserted into this prefix tree
        (compare values using ==), then the given weight should be *added* to
        the existing weight of this value.

        Preconditions:
            weight > 0
            The given value is either:
                1) not in this Autocompleter
                2) was previously inserted with the SAME prefix sequence
        """
        raise NotImplementedError

    def autocomplete(self, prefix: List,
                     limit: Optional[int] = None) -> List[Tuple[Any, float]]:
        """Return up to <limit> matches for the given prefix.

        The return value is a list of tuples (value, weight), and must be
        ordered in non-increasing weight. (You can decide how to break ties.)

        If limit is None, return *every* match for the given prefix.

        Precondition: limit is None or limit > 0.
        """
        raise NotImplementedError

    def remove(self, prefix: List) -> None:
        """Remove all values that match the given prefix.
        """
        raise NotImplementedError


################################################################################
# SimplePrefixTree (Tasks 1-3)
################################################################################
class SimplePrefixTree(Autocompleter):
    """A simple prefix tree.

    This class follows the implementation described on the assignment handout.
    Note that we've made the attributes public because we will be accessing them
    directly for testing purposes.

    === Attributes ===
    value:
        The value stored at the root of this prefix tree, or [] if this
        prefix tree is empty.
    weight:
        The weight of this prefix tree. If this tree is a leaf, this attribute
        stores the weight of the value stored in the leaf. If this tree is
        not a leaf and non-empty, this attribute stores the *aggregate weight*
        of the leaf weights in this tree.
    subtrees:
        A list of subtrees of this prefix tree.
    weight_type:
        The type of accumulated weight being used for internal values in this
        tree.
    size: number of subtrees to this tree

    === Representation invariants ===
    - self.weight >= 0

    - (EMPTY TREE):
        If self.weight == 0, then self.value == [] and self.subtrees == [].
        This represents an empty simple prefix tree.
    - (LEAF):
        If self.subtrees == [] and self.weight > 0, this tree is a leaf.
        (self.value is a value that was inserted into this tree.)
    - (NON-EMPTY, NON-LEAF):
        If len(self.subtrees) > 0, then self.value is a list (*common prefix*),
        and self.weight > 0 (*aggregate weight*).

    - ("prefixes grow by 1")
      If len(self.subtrees) > 0, and subtree in self.subtrees, and subtree
      is non-empty and not a leaf, then

          subtree.value == self.value + [x], for some element x

    - self.subtrees does not contain any empty prefix trees.
    - self.subtrees is *sorted* in non-increasing order of their weights.
      (You can break ties any way you like.)
      Note that this applies to both leaves and non-leaf subtrees:
      both can appear in the same self.subtrees list, and both have a `weight`
      attribute.
    """
    value: Any
    weight: float
    weight_sum: float
    subtrees: List[SimplePrefixTree]
    weight_type: str
    size: int

    def __init__(self, weight_type: str) -> None:
        """Initialize an empty simple prefix tree.

        Precondition: weight_type == 'sum' or weight_type == 'average'.

        The given <weight_type> value specifies how the aggregate weight
        of non-leaf trees should be calculated (see the assignment handout
        for details).
        """
        self.weight_type = weight_type
        self.weight = 0
        self.weight_sum = 0
        self.value = []
        self.subtrees = []
        self.size = 0

    def __len__(self) -> int:
        """Returns the amount of leaves in the tree """
        return self.size

    def insert(self, value: Any, weight: float, prefix: List) -> None:
        """Insert the given value into this Autocompleter.

        The value is inserted with the given weight, and is associated with
        the prefix sequence <prefix>.

        If the value has already been inserted into this prefix tree
        (compare values using ==), then the given weight should be *added* to
                the existing weight of this value.

        Preconditions:
            weight > 0
            The given value is either:
                1) not in this Autocompleter
                2) was previously inserted with the SAME prefix sequence
        """
        self._insert_helper(value, weight, prefix)
        self._update_order(prefix)

    def _insert_helper(self, value: Any, weight: float, prefix: List) -> bool:
        """Main body of insert method"""
        if self.is_empty():
            self.size += 1
            self._adjust_weight(weight)
            self._insert_new(value, weight, prefix, 0)
            return False
        else:
            for subtree in self.subtrees:
                if subtree.value == value:
                    self._adjust_weight(weight)
                    subtree.weight += weight
                    subtree.weight_sum += weight
                    return True
                elif subtree.value == prefix[0:len(subtree.value)]:
                    self.size += 1
                    re_adjust = subtree._insert_helper(value, weight, prefix)
                    self.size -= re_adjust
                    self._adjust_weight(weight)
                    return re_adjust
            self.size += 1
            self._adjust_weight(weight)
            for i in range(len(self.subtrees)):
                if self.subtrees[i].weight <= weight:
                    self._insert_new(value, weight, prefix, i)
                    return False
            self._insert_new(value, weight, prefix, len(self.subtrees))
            return False

    def _insert_new(self, value: Any, weight: float, prefix: List, index: int) \
            -> None:
        """helper function for inserting into a tree"""
        if self.value == prefix:
            self.subtrees.insert(index, _new_subtree_simple(value, weight,
                                                            self.weight_type))
        else:
            insert_tree = _new_subtree_simple(self.value +
                                              [prefix[len(self.value)]],
                                              weight, self.weight_type)
            self.subtrees.insert(index, insert_tree)
            self.subtrees[index]._insert_new(value, weight, prefix, 0)

    def _update_order(self, prefix: list) -> None:
        """update the order of tree in case representation invariants were
        violated
        """
        for i in range(len(self.subtrees)):
            if not isinstance(self.subtrees[i].value, List) or \
                    self.subtrees[i].value == \
                    prefix[:len(self.subtrees[i].value)]:
                for j in range(len(self.subtrees)):
                    if self.subtrees[i].weight > self.subtrees[j].weight \
                            and i != j - 1:
                        self.subtrees.insert(j, self.subtrees.pop(i))
                self.subtrees[i]._update_order(prefix)

    def _adjust_weight(self, weight: float) -> None:
        """adjust the weight and the sum of the weights of the items"""
        self.weight_sum += weight
        if self.weight_type == 'average':
            self.weight = self.weight_sum / self.size
        else:
            self.weight = self.weight_sum

    def is_empty(self) -> bool:
        """Return whether this simple prefix tree is empty."""
        return self.size == 0

    def is_leaf(self) -> bool:
        """Return whether this simple prefix tree is a leaf."""
        return self.weight > 0 and self.subtrees == []

    def __str__(self) -> str:
        """Return a string representation of this tree.

        You may find this method helpful for debugging.
        """
        return self._str_indented()

    def _str_indented(self, depth: int = 0) -> str:
        """Return an indented string representation of this tree.

        The indentation level is specified by the <depth> parameter.
        """
        if self.is_empty():
            return ''
        else:
            s = '  ' * depth + f'{self.value} ({self.weight})\n'
            for subtree in self.subtrees:
                s += subtree._str_indented(depth + 1)
            return s

    def autocomplete(self, prefix: List,
                     limit: Optional[int] = None) -> List[Tuple[Any, float]]:
        """Return up to <limit> matches for the given prefix.
        The return value is a list of tuples (value, weight), and must be
        ordered in non-increasing weight. (You can decide how to break ties.)
        If limit is None, return *every* match for the given prefix.
        Precondition: limit is None or limit > 0.
        """
        result = self._autocomplete_helper(prefix, limit)
        return sorted(result, key=lambda weight: weight[1], reverse=True)

    def _autocomplete_helper(self, prefix: List, limit: Optional[int] = None) \
            -> List[Tuple[Any, float]]:
        """Find the prefix value from autocomplete, and return auto-completed
        values using _iterate_helper
        """
        if self.is_empty():
            return []
        else:
            lst = []
            if self.value == prefix:
                lst += self._iterate_helper(limit)
            elif self.value == prefix[0: len(self.value)]:
                for subtree in self.subtrees:
                    lst += subtree._autocomplete_helper(prefix, limit)
            return lst

    def _iterate_helper(self, limit: Optional[int]) -> List[Tuple[Any, float]]:
        """Return auto-completed values"""
        if self.is_leaf():
            return [(self.value, self.weight)]
        else:
            lst = []
            for subtree in self.subtrees:
                if limit is None or len(lst) < limit:
                    lst.extend(subtree._iterate_helper(limit))
            return lst

    def remove(self, prefix: List) -> None:
        """Remove all values that match the given prefix."""
        if prefix:
            search_list = self._find_last_double(prefix, self)
            if search_list:
                self._change_all_weights(prefix, search_list[0], search_list[1],
                                         search_list[2])
        else:
            self.__init__(self.weight_type)

    def _find_last_double(self, prefix: List,
                          last: Optional[SimplePrefixTree]) -> List:
        """Find last node on the way to the remove value with more than one
        subtree and return list of the size and weight of the child
        """
        if self.is_empty():
            return []
        else:
            lst = []
            if self.value == prefix:
                return [last, self.weight, self.size]
            elif self.value == prefix[:len(self.value)]:
                if len(self.subtrees) > 1:
                    last = self
                for subtree in self.subtrees:
                    lst.extend(subtree._find_last_double(prefix, last))
            return lst

    def _change_all_weights(self, prefix: List, last: SimplePrefixTree,
                            weight_sum: float, removed_size: int) -> None:
        """Remove chosen value from the tree and update all weights of parent
        nodes
        """
        if self.is_empty():
            return
        elif self.value == last.value[:len(self.value)]:
            self.size -= removed_size
            self.weight_sum -= weight_sum
            if self.size <= 0:
                self.weight = 0
            else:
                if self.weight_type == 'average':
                    self.weight = self.weight_sum / self.size
                else:
                    self.weight = self.weight_sum
            if self.value == last.value:
                i = 0
                while i < len(self.subtrees):
                    if self.subtrees[i].value == \
                            prefix[:len(self.subtrees[i].value)]:
                        self.subtrees = self.subtrees[:i] + \
                                        self.subtrees[i+1:]
                    else:
                        i += 1
            else:
                for subtree in self.subtrees:
                    subtree._change_all_weights(prefix, last, weight_sum,
                                                removed_size)


def _new_subtree_simple(value: Any, weight: float, weight_type: str) -> \
        SimplePrefixTree:
    """helper function for returning a subtree with assigned values"""
    subtree = SimplePrefixTree(weight_type)
    subtree.value = value
    subtree.weight = weight
    subtree.weight_sum = weight
    subtree.size = 1
    return subtree


################################################################################
# CompressedPrefixTree (Task 6)
################################################################################
class CompressedPrefixTree(SimplePrefixTree):
    """A compressed prefix tree implementation.

    While this class has the same public interface as SimplePrefixTree,
    (including the initializer!) this version follows the implementation
    described on Task 6 of the assignment handout, which reduces the number of
    tree objects used to store values in the tree.

    === Attributes ===
    value:
        The value stored at the root of this prefix tree, or [] if this
        prefix tree is empty.
    weight:
        The weight of this prefix tree. If this tree is a leaf, this attribute
        stores the weight of the value stored in the leaf. If this tree is
        not a leaf and non-empty, this attribute stores the *aggregate weight*
        of the leaf weights in this tree.
    subtrees:
        A list of subtrees of this prefix tree.

    === Representation invariants ===
    - self.weight >= 0

    - (EMPTY TREE):
        If self.weight == 0, then self.value == [] and self.subtrees == [].
        This represents an empty simple prefix tree.
    - (LEAF):
        If self.subtrees == [] and self.weight > 0, this tree is a leaf.
        (self.value is a value that was inserted into this tree.)
    - (NON-EMPTY, NON-LEAF):
        If len(self.subtrees) > 0, then self.value is a list (*common prefix*),
        and self.weight > 0 (*aggregate weight*).

    - **NEW**
      This tree does not contain any compressible internal values.
      (See the assignment handout for a definition of "compressible".)

    - self.subtrees does not contain any empty prefix trees.
    - self.subtrees is *sorted* in non-increasing order of their weights.
      (You can break ties any way you like.)
      Note that this applies to both leaves and non-leaf subtrees:
      both can appear in the same self.subtrees list, and both have a `weight`
      attribute.
    """
    value: Optional[Any]
    weight: float
    subtrees: List[CompressedPrefixTree]
    weight_sum: float
    weight_type: str
    size: int

    def __init__(self, weight_type: str) -> None:
        """Initialize an empty simple prefix tree.

        Precondition: weight_type == 'sum' or weight_type == 'average'.

        The given <weight_type> value specifies how the aggregate weight
        of non-leaf trees should be calculated (see the assignment handout
        for details).
        """
        SimplePrefixTree.__init__(self, weight_type)

    def _insert_helper(self, value: Any, weight: float, prefix: List) -> bool:
        """Main body of insert method"""
        if self.is_empty():
            self.size += 1
            self._insert_new(value, weight, prefix, 0)
            return False
        else:
            for subtree in self.subtrees:
                if subtree.value == value:
                    self._adjust_weight(weight)
                    subtree.weight += weight
                    subtree.weight_sum += weight
                    return True
                elif subtree.value == prefix[:len(subtree.value)]:
                    self.size += 1
                    re_adjust = subtree._insert_helper(value, weight, prefix)
                    self.size -= re_adjust
                    self._adjust_weight(weight)
                    return re_adjust
                elif isinstance(subtree.value, list) and subtree.value[0] \
                        == prefix[0]:
                    self.size += 1
                    self._compress_helper(subtree, value, weight,
                                          prefix)
                    return False
            self.size += 1
            for i in range(len(self.subtrees)):
                if self.subtrees[i].weight <= weight:
                    self._insert_new(value, weight, prefix, i)
                    return False
            self._insert_new(value, weight, prefix, len(self.subtrees))
            return False

    def _compress_helper(self, subtree: CompressedPrefixTree, value: Any,
                         weight: float, prefix: List) -> None:
        """Concatenate subtree and inserted value with a new common parent"""
        for i in range(1, min(len(subtree.value), len(prefix))):
            if subtree.value[i] != prefix[i]:
                self._adjust_weight(weight)
                subtree_index = self.subtrees.index(subtree)
                self.subtrees[subtree_index] = _new_subtree_compressed(
                    prefix[:i], subtree.weight, subtree.weight_type)
                self.subtrees[subtree_index].size = subtree.size
                self.subtrees[subtree_index].subtrees.append(subtree)
                self.subtrees[subtree_index]._insert_new(
                    value, weight, prefix, weight < subtree.weight)
                break


    def _insert_new(self, value: Any, weight: float, prefix: List, index: int) \
            -> None:
        """helper function for inserting into an empty tree"""
        self._adjust_weight(weight)
        self.subtrees.insert(index, _new_subtree_compressed(prefix, weight,
                                                            self.weight_type))
        self.subtrees[index].subtrees.append(_new_subtree_compressed(
            value, weight, self.weight_type))

    def _autocomplete_helper(self, prefix: List, limit: Optional[int] = None) \
            -> List[Tuple[Any, float]]:
        """Find the prefix value from autocomplete, and return auto-completed
        values using _iterate_helper
        """
        if self.is_empty():
            return []
        else:
            lst = []
            if self.value == prefix or (len(self.value) > len(prefix) and
                                        self.value[:len(prefix)] == prefix):
                lst += self._iterate_helper(limit)
            elif self.value == prefix[0: len(self.value)]:
                for subtree in self.subtrees:
                    lst += subtree._autocomplete_helper(prefix, limit)
            return lst

    def _iterate_helper(self, limit: Optional[int]) -> List[Tuple[Any, float]]:
        """Return auto-completed values"""
        if self.is_leaf():
            return [(self.value, self.weight)]
        else:
            lst = []
            for subtree in self.subtrees:
                if limit is None or len(lst) < limit:
                    lst.extend(subtree._iterate_helper(limit))
            return lst

    def remove(self, prefix: List) -> None:
        """Remove all values that match the given prefix."""
        if prefix:
            self._remove_helper(prefix)
        else:
            self.__init__(self.weight_type)

    def _remove_helper(self, prefix: List) -> float:
        if self.is_empty():
            return 0.0
        else:
            for subtree in self.subtrees:
                if subtree.value == prefix or (len(subtree.value) > len(prefix)
                                               and subtree.value[:len(prefix)]
                                               == prefix):
                    self.subtrees.remove(subtree)
                    self.size -= 1
                    self._adjust_weight(-subtree.weight)
                    return subtree.weight
                elif subtree.value == prefix[:len(subtree.value)]:
                    re_adjust = subtree._remove_helper(prefix)
                    self.size -= 1
                    self._adjust_weight(-re_adjust)
                    return re_adjust
            return 0.0


def _new_subtree_compressed(value: Any, weight: float, weight_type: str) -> \
        CompressedPrefixTree:
    """helper function for returning a subtree with assigned values"""
    subtree = CompressedPrefixTree(weight_type)
    subtree.value = value
    subtree.weight = weight
    subtree.weight_sum = weight
    subtree.size = 1
    return subtree


if __name__ == '__main__':
    import python_ta
    python_ta.check_all(config={
        'max-nested-blocks': 4
    })
