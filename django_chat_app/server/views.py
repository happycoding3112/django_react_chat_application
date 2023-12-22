from django.db.models import Count

from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import ValidationError, AuthenticationFailed

from .models import Server
from .serializers import ServerSerializer
from .schema import server_list_docs


class ServerListViewSet(viewsets.ViewSet):
    """
    A viewset for handling Server objects, providing filtering and serialization.

    Attributes:
    queryset (QuerySet): The default queryset for the view, including all Server objects.

    Methods:
    list(request): Retrieve and serialize a list of Server objects based on query parameters.

    Examples:
    To get a list of servers with additional information about the number of members:
    ```
    GET /servers/?with_num_members=true
    ```

    To filter servers by a specific category name:
    ```
    GET /servers/?category=example_category
    ```

    To limit the number of servers returned:
    ```
    GET /servers/?qty=5
    ```

    To filter servers by the current user:
    ```
    GET /servers/?by_user=true
    ```

    To filter servers by a specific server ID:
    ```
    GET /servers/?by_serverid=123
    ```

    Raises:
    AuthenticationFailed: If authentication is required, and the user is not authenticated.

    ValidationError: If there are issues with provided parameters or if the specified server ID does not exist.

    """

    # Set the default queryset for the view to include all Server objects
    queryset = Server.objects.all()

    @server_list_docs
    def list(self, request):
        # Retrieve query parameters from the request
        category = request.query_params.get("category")
        by_user = request.query_params.get("by_user") == "true"
        by_serverid = request.query_params.get("by_serverid")
        qty = request.query_params.get("qty")
        with_num_members = request.query_params.get("with_num_members") == "true"

        # Check if authentication is required and user is not authenticated
        if (by_user or by_serverid) and not request.user.is_authenticated:
            raise AuthenticationFailed()

        # Apply filters based on query parameters
        if category:
            self.queryset = self.queryset.filter(category__name=category)

        # Filter servers by the current user if `by_user` parameter is provided
        if by_user:
            user_id = request.user.id
            self.queryset = self.queryset.filter(member=user_id)

        # Include the number of members in each server if `with_num_members` is True
        if with_num_members:
            self.queryset = self.queryset.annotate(num_members=Count("member"))

        # Limit the number of servers returned if `qty` parameter is provided
        if qty:
            self.queryset = self.queryset[: int(qty)]

        # Filter servers by server ID if `by_serverid` parameter is provided
        if by_serverid:
            try:
                # Attempt to filter the queryset by server ID
                self.queryset = self.queryset.filter(id=by_serverid)

                # Raise an error if the server with the provided ID does not exist
                if not self.queryset.exists():
                    raise ValidationError(
                        detail=f"Server with id {by_serverid} does not exist!"
                    )
            except:
                # Raise an error for any unexpected issues with the provided server ID
                raise ValidationError(detail=f"Server value error!")

        # Serialize the queryset and return the response
        serializer = ServerSerializer(
            self.queryset,
            many=True,
            context={"num_members": with_num_members},
        )
        return Response(serializer.data, status=status.HTTP_200_OK)
