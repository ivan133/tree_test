#encoding: utf-8
from django.test import TestCase
from tree_model.factories import RegionFactory
from tree_model.models import Region


class TreeModelTests(TestCase):
    def setUp(self):
        #обычно тесты выполняются независимо от окружения
        #но для демонстрации примеров я всегда здесь создаю
        #одинаковую структуру
        #
        # root
        #     child_1
        #         child_1_1
        #         child_1_2
        #         child_1_3
        #         child_1_4
        #         child_1_5
        #     child_2
        #         child_2_1
        #             child_2_1_1
        #             child_2_1_2
        #         child_2_2
        #     child_3
        #TODO написать генератор, который будет генерировать это дерево и расставаять имена
        self.root = RegionFactory(title='root')
        self.child_1 = RegionFactory(parent=self.root, title='child_1')
        self.child_1_1 = RegionFactory(parent=self.child_1, title='child_1_1')
        self.child_1_2 = RegionFactory(parent=self.child_1, title='child_1_2')
        self.child_1_3 = RegionFactory(parent=self.child_1, title='child_1_3')
        self.child_1_4 = RegionFactory(parent=self.child_1, title='child_1_4')
        self.child_1_5 = RegionFactory(parent=self.child_1, title='child_1_5')
        self.child_2 = RegionFactory(parent=self.root, title='child_2')
        self.child_2_1 = RegionFactory(parent=self.child_2, title='child_2_1')
        self.child_2_1_1 = RegionFactory(parent=self.child_2_1, title='child_2_1_1')
        self.child_2_1_2 = RegionFactory(parent=self.child_2_1, title='child_2_1_2')
        self.child_2_2 = RegionFactory(parent=self.child_2, title='child_2_2')
        self.child_3 = RegionFactory(parent=self.root, title='child_3')

    def test_get_root(self):
        RegionFactory(parent=self.root)
        Region.objects.get(parent=None)
        self.assertEqual(self.root, Region.objects.get_root())

    def test_get_depth_root(self):
        self.assertEqual(self.root.get_depth(), 1)

    def test_get_depth_children(self):
        self.child_1 = RegionFactory(parent=self.root)
        self.assertEqual(self.child_1.get_depth(), 2)
        self.child_2 = RegionFactory(parent=self.child_1)
        self.assertEqual(self.child_2.get_depth(), 3)

    def test_get_siblings(self):
        self.assertEqual(list(self.child_1_3.get_siblings()), [self.child_1_1, self.child_1_2, self.child_1_3,
                                                               self.child_1_4, self.child_1_5])

        self.assertEqual(self.child_1_3.get_first_sibling(), self.child_1_1)
        self.assertEqual(self.child_1_3.get_last_sibling(), self.child_1_5)
        self.assertEqual(self.child_1_1.get_previous_sibling(), None)
        self.assertEqual(self.child_1_5.get_next_sibling(), None)
        self.assertEqual(self.child_1_3.get_next_sibling(), self.child_1_4)
        self.assertEqual(self.child_1_3.get_previous_sibling(), self.child_1_2)

    def test_get_children(self):
        self.assertEqual(list(self.root.get_children()), [self.child_1, self.child_2, self.child_3])
        self.assertEqual(self.root.get_children_count(), 3)
        self.assertEqual(self.root.get_first_child(), self.child_1)
        self.assertEqual(self.root.get_last_child(), self.child_3)

    def test_get_ancestors(self):
        self.assertEqual(list(self.root.get_ancestors()), [])
        self.assertEqual(list(self.child_1.get_ancestors()), [self.root])
        self.assertEqual(list(self.child_1_2.get_ancestors()), [self.root, self.child_1])
        self.assertEqual(list(self.child_2_1_2.get_ancestors()), [self.root, self.child_2, self.child_2_1])

    def test_get_descendants(self):
        self.assertEqual(list(self.child_1.get_descendants()), [self.child_1_1, self.child_1_2, self.child_1_3, self.child_1_4, self.child_1_5])
        self.assertEqual(self.child_1.get_children_count(), self.child_1.get_descendant_count())

        # а теперь с детьми детей
        self.assertEqual(list(self.child_2.get_descendants()), [self.child_2_1, self.child_2_1_1, self.child_2_1_2, self.child_2_2])

    def test_get_tree(self):
        region_tree = Region.objects.get_tree()
        ethalon_tree = [self.root, self.child_1, self.child_1_1,
             self.child_1_2, self.child_1_3, self.child_1_4, self.child_1_5, self.child_2,
             self.child_2_1, self.child_2_1_1, self.child_2_1_2,
             self.child_2_2, self.child_3]
        self.assertEqual(region_tree, ethalon_tree)
        self.assertEqual(Region.objects.get_tree(self.child_2), [self.child_2, self.child_2_1, self.child_2_1_1,
                                                            self.child_2_1_2, self.child_2_2])

    def test_relations(self):
        self.assertTrue(self.child_1_1.is_sibling_of(self.child_1_2))
        self.assertFalse(self.child_1_1.is_sibling_of(self.child_2_1))
        self.assertFalse(self.child_1_1.is_sibling_of(self.root))

        self.assertTrue(self.child_1.is_child_of(self.root))
        self.assertTrue(self.child_1_1.is_child_of(self.child_1))
        self.assertTrue(self.child_2_1_1.is_child_of(self.child_2_1))
        self.assertFalse(self.child_2_1_1.is_child_of(self.child_2_2))

        self.assertTrue(self.child_1.is_descendant_of(self.root))
        self.assertTrue(self.child_2_1_2.is_descendant_of(self.root))
        self.assertTrue(self.child_2_1_2.is_descendant_of(self.child_2_1))
        self.assertFalse(self.child_2_1_2.is_descendant_of(self.child_2_1_1))

        self.assertTrue(self.root.is_root())
        self.assertFalse(self.child_2_1_2.is_root())

