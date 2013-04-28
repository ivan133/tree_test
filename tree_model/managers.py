#encoding: utf-8
from django.db import models


class TreeNodeManager(models.Manager):

    def get_query_set(self):
        "Добавляем сортировку по нодам в QuerySet"
        return super(TreeNodeManager, self).get_query_set().order_by('parent', self.model.node_order)

    def get_root(self):
        """
        вернуть вершину дерева
        """
        return self.get(parent=None)

    def get_tree(self, parent=None):
        """
        :returns: Список нодов в порядке сортировки, относительно

        :param parent: Нод, относительно которого стоить дерево
        """
        if parent:
            depth = parent.get_depth() + 1
            result = [parent]
        else:
            depth = 1
            result = []
        self._get_tree(result, parent, depth)
        return result

    def _get_tree(self, result, parent, depth):
        """
        :returns: список нодов

        :param result: результат куда добавлять данные
        :param parent: Родитель относительно которго сторить девево
        :param depth: Уровень (глубина дерева)
        """
        if parent:
            query_set = self.filter(parent=parent)
        else:
            query_set = self.filter(pk=self.get_root().pk)
        for node in query_set:
            node._cached_depth = depth
            result.append(node)
            self._get_tree(result, node, depth + 1)