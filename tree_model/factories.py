#encoding: utf-8
import factory
from tree_model.models import Region


class RegionFactory(factory.Factory):
    FACTORY_FOR = Region
    title = factory.Sequence(lambda n: u'Region{0}'.format(n))
    parent = None
    #FIXME HACK на моей базе почему то не сохраняется, по этому примерним такой хак
    @factory.post_generation
    def save_anyway(self, create, extracted, **kwargs):
        self.save()