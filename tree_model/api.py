from tastypie.resources import ModelResource
from tree_model.models import Region


class RegionResource(ModelResource):

    class Meta:
        detail_allowed_methods = ['get']
        queryset = Region.objects.all()
        resource_name = 'region'