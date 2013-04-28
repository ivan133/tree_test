#encoding: utf-8
from django.db import models
from tree_model.managers import TreeNodeManager


class TreeNode(models.Model):
    u"""
        Модель внутри которой может быть образована иерархия
        parent - ссылка на родителя, на эту же модель для образования дерева
    """
    parent = models.ForeignKey('self', null=True, blank=True, related_name='children')
    #Чтобы работала сотрировака нодов, на одном уровне иерархии в наседнике нужно задать node_order
    objects = TreeNodeManager()

    class Meta:
        abstract = True

    def get_depth(self, update=False):
        """
        :returns: Глубина (уровень) для данного нода относительно root
            для рута 1
            кеширует резульата в переменную _cached_depth

        :param update: Принудительно обновить кеш.
        """
        #это root
        if self.parent_id is None:
            return 1

        try:
            if update:
                del self._cached_depth
            else:
                return self._cached_depth
        except AttributeError:
            pass

        depth = 0
        node = self
        while node:
            node = node.parent
            depth += 1
        self._cached_depth = depth
        return depth

    def get_siblings(self):
        """
        :returns: QuerySet отпрысков (нодов на одном уровне иерархии с текущим
        """
        return self.__class__.objects.filter(parent=self.parent)

    def get_first_sibling(self):
        """
        :returns: Первый отпрыск в списке (сортировка по node_order)
        """
        return self.get_siblings()[0]

    def get_last_sibling(self):
        """
        :returns: Последний отпрыск в списке
        """
        return self.get_siblings().reverse()[0]

    def get_previous_sibling(self):
        """
        :returns: Предыдущий отпрыск или None
        """

        siblings = self.get_siblings()
        ids = [obj.pk for obj in siblings]
        if self.pk in ids:
            idx = ids.index(self.pk)
            if idx > 0:
                return siblings[idx - 1]
        return None

    def get_next_sibling(self):
        """
        :returns: Следующий отпрыск или None
        """
        siblings = self.get_siblings()
        ids = [obj.pk for obj in siblings]
        if self.pk in ids:
            idx = ids.index(self.pk)
            if idx < len(siblings) - 1:
                return siblings[idx + 1]
        return None

    def get_children(self):
        """
        :returns: Queryset со всем детьми нода
        """
        return self.children.all()

    def get_children_count(self):
        """
        :returns: Количество детей
        """
        return self.get_children().count()

    def get_first_child(self):
        """
        :returns: первый ребенок по порядку.
        Или None
        """
        try:
            return self.get_children()[0]
        except IndexError:
            return None

    def get_last_child(self):
        """
        :returns: Последний ребенок по порядку
        """
        try:
            return self.get_children().reverse()[0]
        except IndexError:
            return None

    def get_descendants(self):
        """
        :returns: Список потомоков - все дети данного нода
        """
        return self.__class__.objects.get_tree(parent=self)[1:]

    def get_descendant_count(self):
        """
        :returns: колчиество потомков
        """
        return len(self.get_descendants())

    def get_root(self):
        """
        :returns: вернуть вершину дерева
        считаем, что рут есть и только 1 так как у нас дерево
        """
        return self.__class__.objects.get_root()

    def get_ancestors(self):
        """
        :returns: список предков (родители до самого рута)
        """
        ancestors = []
        node = self.parent
        while node:
            ancestors.append(node)
            node = node.parent
        ancestors.reverse()
        return ancestors

    def get_parent(self, update=False):
        """
        :returns: Возвращет родителя текушего нода.

        :param update: Обновить закешированное значение.
        """
        try:
            if update:
                del self._cached_parent
            else:
                return self._cached_parent
        except AttributeError:
            #если параметра нет ничего страшного _cached_parent
            pass
        self._cached_parent = self.__class__.objects.get(pk=self.parent)
        return self._cached_parent

    def is_sibling_of(self, node):
        """
        :returns: Проверяет явлется нод отпрыском

        :param node: Нод который нужно проверить
        """
        return len(self.get_siblings().filter(pk__in=[node.pk])) > 0

    def is_child_of(self, node):
        """
        :returns: Проверяет явлется нод наследником node

        :param node: Нод, чьим наследником он может быть
        """
        return len(node.get_children().filter(pk__in=[self.pk])) > 0

    def is_descendant_of(self, node):
        """
        :returns: Проверяет явлется нод потомком node

        :param node: Нод, который модет быть предком
        """
        #так как get_descendants возвращет список, а не QuerySet примернякм filter
        return len(filter(lambda x: x.pk == self.pk, node.get_descendants())) > 0

    def is_root(self):
        return self.get_root() == self


#Для примера создал модель регионов
class Region(TreeNode):
    title = models.CharField(max_length=256, null=False)
    #нужно казать поле для сортировки
    node_order = 'title'

    def __unicode__(self):
        return '{0} {1}'.format(self.title, self.parent_id)
