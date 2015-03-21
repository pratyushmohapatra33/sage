"""
Automatic monoids.

AUTHORS:

- Nicolas M. Thiery
- Aladin Virmaux
"""

#*****************************************************************************
#  Copyright (C) 2015 Nicolas M. Thiery
#
#  Distributed under the terms of the GNU General Public License (GPL)
#
#    This code is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty
#    of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#
#  See the GNU General Public License for more details; the full text
#  is available at:
#
#                  http://www.gnu.org/licenses/
#*****************************************************************************

from sage.misc.all import cached_method
from sage.categories.all import Monoids
from sage.structure.parent import Parent
from sage.structure.unique_representation import UniqueRepresentation
from sage.structure.element_wrapper import ElementWrapper
from sage.sets.family import Family
from sage.rings.integer import Integer
import operator

class AutomaticMonoid(UniqueRepresentation, Parent):
    r"""
    Construct (lazily) a monoid from a set of concrete generators
    living in an ambient monoid.

    EXAMPLES::

        sage: R = IntegerModRing(12)
        sage: M = AutomaticMonoid(Family({1: R(3), 2: R(5)}), one = R.one())
        sage: M.one()
        []
        sage: M.one() in M
        True

    Elements are represented by default by their reduced word, or by
    the corresponding element in the ambient monoid if the reduced
    word is not yet known.

    ::

        sage: g = M.generators; g
        Finite family {1: [1], 2: [2]}
        sage: g[1]*g[2]
        [1]

    Calling cardinality, or list, or iterating through the monoid will
    trigger its full construction and, as a side effect, compute all
    the reduced words. The order of the elements, and the induced
    choice of reduced word is currently length-lexicographic
    (i.e. the chosen reduced word is of minimal length, and then
    minimal lexicographically w.r.t. the order of the indices of the
    generators)::

        sage: M.cardinality()
        4
        sage: M.list()
        [[], [1], [2], [1, 1]]
        sage: g = M.generators

        sage: g[1]*g[2]
        [1]

        sage: g[1].transition(1)
        [1, 1]
        sage: g[1] * g[1]
        [1, 1]
        sage: g[1] * g[1] * g[1]
        [1]
        sage: g[1].transition(2)
        [1]
        sage: g[1] * g[2]
        [1]
        sage: M.list()
        [[], [1], [2], [1, 1]]
        sage: [ x.lift() for x in M.list() ]
        [1, 3, 5, 9]
        sage: M.idempotents()
        [[], [1, 1]]
        sage: G = M.cayley_graph(side = "twosided"); G
        Looped multi-digraph on 4 vertices
        sage: sorted(G.edges(), key=str)
        [([1, 1], [1, 1], (2, 'left')),
         ([1, 1], [1, 1], (2, 'right')),
         ([1, 1], [1], (1, 'left')),
         ([1, 1], [1], (1, 'right')),
         ([1], [1, 1], (1, 'left')),
         ([1], [1, 1], (1, 'right')),
         ([1], [1], (2, 'left')),
         ([1], [1], (2, 'right')),
         ([2], [1], (1, 'left')),
         ([2], [1], (1, 'right')),
         ([2], [], (2, 'left')),
         ([2], [], (2, 'right')),
         ([], [1], (1, 'left')),
         ([], [1], (1, 'right')),
         ([], [2], (2, 'left')),
         ([], [2], (2, 'right'))]
        sage: map(sorted, M.j_classes())
        [[[], [2]], [[1, 1], [1]]]
        sage: M.j_classes_of_idempotents()
        [[[]], [[1, 1]]]
        sage: M.j_transversal_of_idempotents()
        [[], [1, 1]]

        sage: map(attrcall('pseudo_order'), M.list())
        [[1, 0], [3, 1], [2, 0], [2, 1]]

    We can also use it to get submonoids from groups. We check that in the
    symmetric group, a transposition and a cyle generate the whole group::

        sage: G5 = SymmetricGroup(5)
        sage: N = AutomaticMonoid(Family({1: G5([2,1,3,4,5]), 2: G5([2,3,4,5,1])}), G5.one())
        sage: N.cardinality() == G5.cardinality()
        True
        sage: N.retract(G5((1,4,3,5,2)))
        [1, 2, 1, 2, 2, 1, 2, 1, 2, 2]
        sage: N.from_reduced_word([1, 2, 1, 2, 2, 1, 2, 1, 2, 2]).lift()
        (1,4,3,5,2)

   We can also create a monoid of matrices, where we define the multiplication as matrix
    multiplication::

        sage: M1=matrix([[0,0,1],[1,0,0],[0,1,0]])
        sage: M2=matrix([[0,0,0],[1,1,0],[0,0,1]])
        sage: M1.set_immutable()
        sage: M2.set_immutable()
        sage: def prod_m(x,y):
        ....:     z=x*y
        ....:     z.set_immutable()
        ....:     return z
        ....:
        sage: Mon = AutomaticMonoid([M1,M2], mul=prod_m)
        sage: Mon.cardinality()
        24
        sage: Mon.one()
        []

    Let us construct and play with the 0-Hecke Monoid::

        sage: W = WeylGroup(['A',4])
        sage: ambient_monoid = FiniteSetMaps(W, action="right")
        sage: pi = W.simple_projections(length_increasing=True).map(ambient_monoid)
        sage: M = AutomaticMonoid(pi, one=ambient_monoid.one()); M
        The (automatic) monoid with generators Finite family {1: [1], 2: [2],
        3: [3], 4: [4]}
        sage: sorted(M.elements_set, key=str)
        [[1], [2], [3], [4], []]
        sage: M.compute_n_elements(10)
        sage: sorted(M.elements_set, key=str)
        [[1, 2], [1, 3], [1, 4], [1], [2, 1], [2, 3], [2], [3], [4], []]
        sage: elt = M.from_reduced_word([3,1,2,4,2])
        sage: M.compute_until(elt)
        sage: len(M.elements_set)
        36
        sage: M.cardinality()
        120

    We check that the 0-Hecke monoid is `J`-trivial and contains `2^4`
    idempotents::

        sage: len(M.idempotents())
        16
        sage: all([len(j) == 1 for j in M.j_classes()])
        True

    TESTS::

        sage: (g[1]).__hash__() == (g[1]*g[1]*g[1]).__hash__()
        True
        sage: g[1] == g[1]*g[1]*g[1]
        True
        sage: M.__class__.mro()
        [<class 'sage.monoids.automatic_monoid.AutomaticMonoid_with_category'>, <class 'sage.monoids.automatic_monoid.AutomaticMonoid'>, <class 'sage.structure.unique_representation.UniqueRepresentation'>, <class 'sage.structure.unique_representation.CachedRepresentation'>, <type 'sage.misc.fast_methods.WithEqualityById'>, <type 'sage.structure.parent.Parent'>, <type 'sage.structure.category_object.CategoryObject'>, <type 'sage.structure.sage_object.SageObject'>, <class 'sage.categories.finite_monoids.FiniteMonoids.parent_class'>, <class 'sage.categories.monoids.Monoids.parent_class'>, <class 'sage.categories.finite_semigroups.FiniteSemigroups.parent_class'>, <class 'sage.categories.semigroups.Semigroups.parent_class'>, <class 'sage.categories.magmas.Magmas.Unital.parent_class'>, <class 'sage.categories.magmas.Magmas.parent_class'>, <class 'sage.categories.finite_enumerated_sets.FiniteEnumeratedSets.parent_class'>, <class 'sage.categories.enumerated_sets.EnumeratedSets.parent_class'>, <class 'sage.categories.finite_sets.FiniteSets.parent_class'>, <class 'sage.categories.sets_cat.Sets.parent_class'>, <class 'sage.categories.sets_with_partial_maps.SetsWithPartialMaps.parent_class'>, <class 'sage.categories.objects.Objects.parent_class'>, <type 'object'>]
        sage: TestSuite(M).run()

    We need to pass in the ambient monoid to ``__init__`` to guarantee
    :class:`UniqueRepresentation` works properly::

        sage: R1 = IntegerModRing(12)
        sage: R2 = IntegerModRing(16)
        sage: M1 = AutomaticMonoid(Family({1: R1(3), 2: R1(5)}), one = R1.one())
        sage: M2 = AutomaticMonoid(Family({1: R2(3), 2: R2(5)}), one = R2.one())
        sage: M1 is M2
        False

    CAVEATS:

    - AutomaticMonoid is designed primarily for finite monoids. This
      property is not checked automatically (this would be too costly
      if not impossible). Some of the features should still work with
      infinite monoids. In that case, the category Monoids() should
      be passed as extra argument, instead of the default
      Monoids().Finite().

    ::

        sage: AutomaticMonoid(Family({1:2}), category = Monoids().Finite())
        The (automatic) monoid with generators Finite family {1: [1]}

    BUGS:

    - Running a command like [ f(p) for p in M ] where f involves
      computing products of elements and M.list() has not yet been
      computed caused an infinite loop at least in one occasion looking like::

         sage: all(operator.sub(*p.pseudo_order())==1 for p in M)
         True

    """
    @staticmethod
    def __classcall_private__(cls, generators, ambient=None, one=None, mul=operator.mul, category=Monoids().Finite()):
        """
        TESTS::

            sage: R = IntegerModRing(21)
            sage: M = AutomaticMonoid((), one = R.one())
            sage: M.ambient() == R
            True
        """
        generators = Family(generators)
        if ambient is None:
            # Try to guess the ambient monoid from the generators or the unit
            if generators.cardinality() > 0:
                ambient = generators.first().parent()
            elif one is not None:
                ambient = one.parent()
            else:
                raise ValueError("AutomaticMonoid requires at least one generator or `one` to determine the ambient space")
        return super(AutomaticMonoid, cls).__classcall__(cls, generators, ambient=ambient, one=one, mul=mul, category=category)

    def __init__(self, generators, ambient, one=None, mul=operator.mul, category=Monoids().Finite()):
        """
        TESTS::

            sage: R = IntegerModRing(21)
            sage: M = AutomaticMonoid(Family(()), one = R.one())
            sage: M.ambient() == R
            True
            sage: M = AutomaticMonoid(Family(()))
            Traceback (most recent call last):
            ...
            ValueError: AutomaticMonoid requires at least one generator or `one` to determine the ambient space
        """
        Parent.__init__(self, category=category)
        self.generators = generators                    # todo: rename to self._generators?
        self._ambient = ambient

        if one is None:
            one = self.generators.first().parent().one()
        self._one = self.retract(one)
        self.mul = mul
        self.generators_in_ambient = generators
        self.generators = generators.map(self.retract)

        self.elements     = [self.one()] + list(self.generators)
        self.elements_set = set(self.elements)

        # Reduced word of the identity and generators
        self.one()._reduced_word = []
        for e in self.generators:
            e._reduced_word = [self.generators.inverse_family()[e]]
        self.done= 0

    def one(self):
        """
        Return one of ``self``.

        EXAMPLES::

            sage: R = IntegerModRing(21)
            sage: M = AutomaticMonoid((), one = R.one())
            sage: M.one()
            []
        """
        return self._one

    def _repr_(self):
        """
        EXAMPLES::

            sage: R = IntegerModRing(12)
            sage: M = AutomaticMonoid(Family({1: R(3), 2: R(5)}), one = R.one()); M
            The (automatic) monoid with generators Finite family {1: [1], 2: [2]}
        """
        return "The (automatic) monoid with generators %s"%self.generators

    def an_element(self):
        """
        Return the first given generator of ``self``.

        EXAMPLES::

            sage: R = IntegerModRing(16)
            sage: M = AutomaticMonoid(Family({1: R(3), 2: R(5)}), one = R.one())
            sage: M.cardinality()
            8
            sage: M.an_element()
            [1]
        """
        return self.generators.first()

    def some_elements(self):
        """
        Return the familiy of generators of ``self``.

        EXAMPLES::

            sage: R = IntegerModRing(12)
            sage: M = AutomaticMonoid(Family({1: R(3), 2: R(5)}), one = R.one())
            sage: M.some_elements()
            Finite family {1: [1], 2: [2]}
        """
        return self.semigroup_generators()

    def ambient(self):
        """
        Return the ambient monoid of ``self``.

        EXAMPLES::

            sage: R = IntegerModRing(12)
            sage: M = AutomaticMonoid(Family({1: R(3), 2: R(5)}), one = R.one())
            sage: M.ambient()
            Ring of integers modulo 12

            sage: M1=matrix([[0,0,1],[1,0,0],[0,1,0]])
            sage: M2=matrix([[0,0,0],[1,1,0],[0,0,1]])
            sage: M1.set_immutable()
            sage: M2.set_immutable()
            sage: def prod_m(x,y):
            ....:     z=x*y
            ....:     z.set_immutable()
            ....:     return z
            ....:
            sage: Mon = AutomaticMonoid([M1,M2], mul=prod_m)
            sage: Mon.ambient()
            Full MatrixSpace of 3 by 3 dense matrices over Integer Ring
        """
        return self._ambient

    @cached_method
    def retract(self, ambient_element):
        """
        Retract an element of the ambiant monoid into ``self``.

        EXAMPLES::

            sage: G4 = SymmetricGroup(4)
            sage: M = AutomaticMonoid(Family({1:G4((1,2)), 2:G4((1,2,3,4))}), G4.one())
            sage: M.cardinality()
            24
            sage: M.retract(G4((3,1)))
            [2, 1, 2, 2, 1]
        """
        return self.element_class(self, ambient_element)

    def lift(self, x):
        """
        Lift an element of ``self`` into its ambient space.

        EXAMPLES::

            sage: R = IntegerModRing(15)
            sage: M = AutomaticMonoid(Family({1: R(3), 2: R(5)}), one = R.one())
            sage: M.cardinality()
            8
            sage: a = M.an_element()
            sage: a.lift() in R
            True
            sage: a.lift()
            3
            sage: [m.lift() for m in M]
            [1, 3, 5, 9, 0, 10, 12, 6]
        """
        assert(x in self)
        return x.lift()

    def semigroup_generators(self):
        """
        Return the family of generators of ``self``.

        EXAMPLES::

            sage: R = IntegerModRing(28)
            sage: M = AutomaticMonoid(Family({1: R(3), 2: R(5)}), one = R.one())
            sage: M.semigroup_generators()
            Finite family {1: [1], 2: [2]}
        """
        return self.generators

    def __iter__(self):
        """
        Iterator on the elements of ``self``.

        EXAMPLES::

            sage: R = IntegerModRing(18)
            sage: M = AutomaticMonoid([R(3), R(5)], R.one())
            sage: M.__iter__().next()
            []
            sage: list(M)
            [[], [0], [1], [0, 0], [0, 1], [1, 1], [1, 1, 1], [1, 1, 1, 1], [1,
            1, 1, 1, 1]] 

        ALGORITHM:

            Breadth first search on the elements generated by the generators.
            The algorithm stops when all branches have been fully explored.
        """
        for x in self.elements:
            yield x
        while self.done < len(self.elements):
            x = self.elements[self.done]
            for i in self.generators.keys():
                y = x.transition(i)
                if y in self.elements_set:
                    continue
                self.elements.append(y)
                self.elements_set.add(y)
                y._reduced_word = x.reduced_word()+[i]
                yield y
            self.done += 1
        return

    def cardinality(self):
        """
        Return the cardinality of ``self``.

        EXAMPLES::

            sage: R = IntegerModRing(12)
            sage: M = AutomaticMonoid(Family({1: R(3), 2: R(5)}), one = R.one())
            sage: M.cardinality()
            4

        TESTS::

            sage: assert isinstance(M.cardinality(), Integer)  # This did fail at some point
        """
        if self.done == len(self.elements):
            return Integer(self.done)
        else:
            return self._cardinality_from_iterator()

    def __contains__(self, x):
        """
        TESTS::

            sage: R = IntegerModRing(34)
            sage: M = AutomaticMonoid(Family({1: R(3), 2: R(7)}), one = R.one())
            sage: M[3] in M
            True
        """
        try:
            x.reduced_word(computation=True)
            return True
        except ValueError:
            return False

    def product(self, x, y):
        """
        Return the product of two elements in ``self``. It is done by
        retracting the multiplication in the ambient monoid.

        EXAMPLES::

            sage: R = IntegerModRing(12)
            sage: M = AutomaticMonoid(Family({1: R(3), 2: R(5)}), one = R.one())
            sage: a = M[1]
            sage: b = M[2]
            sage: a*b
            [1]
        """
        assert(x in self)
        assert(y in self)
        red = y.reduced_word()
        if red is None:
            return self.retract(self.mul(x.lift(), y.lift()))
        else:
            for i in red:
                x = x.transition(i)
        return x

    def from_reduced_word(self, l):
        """
        Return the element of ``self`` obtained from the reduced word ``l``.

        INPUT:

        - ``l`` -- a list of indices of the generators

        .. NOTE::

            We do not save the given reduced word ``l`` as an attribute of the
            element, as some elements above in the branches may have not been
            explored by the iterator yet.

        EXAMPLES::

            sage: G4 = SymmetricGroup(4)
            sage: M = AutomaticMonoid(Family({1:G4((1,2)), 2:G4((1,2,3,4))}), G4.one())
            sage: M.cardinality()
            24
            sage: M.from_reduced_word([2, 1, 2, 2, 1]).lift()
            (1,3)
            sage: M.from_reduced_word([2, 1, 2, 2, 1]) == M.retract(G4((3,1)))
            True
        """
        result = self.one()
        for i in l:
            result = result.transition(i)
        return result

    def compute_until(self, elt):
        """
        Compute the elements of the monoid ``self`` until finding ``elt``. If
        ``elt`` is not in ``self``, all elements are computed.

        INPUT:

        -``elt`` -- a potential element of ``self``
        
        EXAMPLES::

            sage: W = WeylGroup(['A',3]) 
            sage: ambient_monoid = FiniteSetMaps(W, action="right")
            sage: pi = W.simple_projections(length_increasing=True).map(ambient_monoid)
            sage: M = AutomaticMonoid(pi, one=ambient_monoid.one()); M
            The (automatic) monoid with generators Finite family {1: [1],
            2: [2], 3: [3]}
            sage: sorted(M.elements_set, key=str)
            [[1], [2], [3], []]
            sage: elt = M.from_reduced_word([2,3,1,2])
            sage: M.compute_until(elt)
            sage: len(M.elements_set)
            19
            sage: M.cardinality()
            24
        """
        elt in self
        return

    def compute_n_elements(self, n):
        """
        Compute the first ``n`` elements of the monoid ``self``. If n is bigger
        than the cardinality of ``self``, then all elements of ``self`` are
        computed.
        """
        it = self.__iter__()
        for x in range(n):
            try:
                it.next()
            except ValueError:
                return
        return

    class Element(ElementWrapper):

        def __init__(self, ambient_element, parent):
            """
            TESTS::

                sage: R = IntegerModRing(21)
                sage: M = AutomaticMonoid(Family(()), one = R.one())
                sage: m = M(2); m
                2
                sage: type(m)
                <class 'sage.monoids.automatic_monoid.AutomaticMonoid_with_category.element_class'>
            """
            ElementWrapper.__init__(self, ambient_element, parent)
            self._reduced_word = None

        def reduced_word(self, computation=False):
            """
            Return the reduced word of ``self``.

            INPUT:

            - ``computation`` -- (default: ``False``) if ``True``, forces the
              computation of the reduced word.

            OUTPUT:

            - The length-lexicographic shortest reduced word for
              ``self``, or None if it has not yet been computed.

            ALGORITHM:

            If ``computation`` is set to True and the reduced word is ``None``,
            an iteration on the elements of the parent is made until finding
            ``self``.

            EXAMPLES::

                sage: R = IntegerModRing(15)
                sage: M = AutomaticMonoid(Family({1: R(3), 2: R(5)}), one = R.one())
                sage: a = M.an_element()
                sage: a.reduced_word(computation=True)
                [1]
                sage: b = M.retract(R(4))
                sage: b.reduced_word(computation=True)
                Traceback (most recent call last):
                ...
                ValueError: 4 is not in The (automatic) monoid with generators Finite family {1: [1], 2: [2]}
            """
            if (self._reduced_word is not None) or (not computation):
                return self._reduced_word
            for x in self.parent():
                if x is self:
                    return self._reduced_word
            raise ValueError("%s is not in %s"%(self, self.parent()))

        def lift(self):
            """
            Lift the element ``self`` into its ambient monoid.

            EXAMPLES::

                sage: R = IntegerModRing(18)
                sage: M = AutomaticMonoid(Family({1: R(3), 2: R(5)}), one = R.one())
                sage: m = M.an_element(); m
                [1]
                sage: type(m)
                <class 'sage.monoids.automatic_monoid.AutomaticMonoid_with_category.element_class'>
                sage: m.lift()
                3
                sage: type(m.lift())
                <type 'sage.rings.finite_rings.integer_mod.IntegerMod_int'>
            """
            return self.value

        @cached_method
        def transition(self, i):
            """
            The multiplication on the right by a generator.

            INPUT:

            - ``i`` -- an element from the indexing set of the generators

            This method computes ``self * self.generators[i]``.

            EXAMPLES::

                sage: R = IntegerModRing(17)
                sage: M = AutomaticMonoid(Family({1: R(3), 2: R(5)}), one = R.one())
                sage: M.cardinality()
                16
                sage: a = M.an_element()
                sage: a.transition(1)
                [1, 1]
                sage: a.transition(2)
                [1, 2]
            """
            parent = self.parent()
            assert(i in parent.generators.keys())
            return parent.retract(parent.mul(self.lift(), parent.generators_in_ambient[i]))

        def _repr_(self):
            """
            EXAMPLES::

                sage: R = IntegerModRing(18)
                sage: M = AutomaticMonoid(Family({1: R(3), 2: R(5)}), one = R.one())
                sage: a = M.an_element(); a
                [1]
                sage: b = M.from_reduced_word([1,2,1]); b
                9
                sage: c = M.retract(R(6)); c
                6
                sage: c in M
                False
            """
            rep = self.reduced_word()
            if rep is None:
                rep = self.lift()
            return str(rep)

        def __copy__(self, memo=None):
            r"""
            Return ``self`` since this has unique representation.

            INPUT:

            - ``memo`` -- ignored, but required by the deepcopy API

            EXAMPLES::

                sage: R = IntegerModRing(12)
                sage: M = AutomaticMonoid(Family({1: R(3), 2: R(5)}), one = R.one())
                sage: m = M.an_element()
                sage: copy(m) is m
                True
                sage: from copy import deepcopy
                sage: deepcopy(m) is m
                True
            """
            return self

        __deepcopy__ = __copy__
