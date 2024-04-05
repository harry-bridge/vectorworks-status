from rest_framework import serializers, status, permissions, viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from status import models

# -------------------------------------------------------------
# Serialisers
# -------------------------------------------------------------
class LicenseInUseSerialiser(serializers.ModelSerializer):
    class Meta:
        model = models.RlmInfo
        fields = ['product', 'version', 'count', 'in_use', 'last_updated']


class LicenseUsageSerialiser(serializers.ModelSerializer):
    class Meta:
        model = models.UserLicenseUsage
        fields = ['user_name', 'host_name', 'version', 'checkout_stamp']


# -------------------------------------------------------------
# REST views
# -------------------------------------------------------------
class LicenseInUseListView(viewsets.ReadOnlyModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    queryset = models.RlmInfo.objects.all()
    serializer_class = LicenseInUseSerialiser


class LicenseInUseDetailView(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def retrieve(self, request, product=None):
        queryset = models.RlmInfo.objects.all()
        product_result = get_object_or_404(queryset, product=product)
        serialiser = LicenseInUseSerialiser(product_result)
        return Response(serialiser.data, status=status.HTTP_200_OK)


class LicenseUsageTopListView(viewsets.ReadOnlyModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    queryset = models.UserLicenseUsage.objects.all().order_by('-checkout_stamp')
    serializer_class = LicenseUsageSerialiser
