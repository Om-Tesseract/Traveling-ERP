from rest_framework import generics, status
from rest_framework.response import Response

class BaseListCreateAPIView(generics.ListCreateAPIView):

    def post(self, request, *args, **kwargs):
        res=super().post(request, *args, **kwargs)
        if res.status_code ==201:
            return Response({ "message": "Record Created Successfully.", "data": res.data},
                            headers=res.headers,
                            status=res.status_code,
                            template_name=res.template_name,
                            exception=res.exception,
                            content_type=res.content_type
                            )
        return res 
    def perform_create(self, serializer):
        if hasattr(serializer.instance, 'created_by'):
            # Set 'created_by' to the current user or null if the user is anonymous
            user = self.request.user
            serializer.save(updated_by=user if user.is_authenticated else None)
       
        return super().perform_create(serializer)

class BaseRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    def put(self, request, *args, **kwargs):
        res=super().put(request, *args, **kwargs)
        if res.status_code ==200:
            return Response({ "message": "Record Updated Successfully.", "data": res.data},
                            headers=res.headers,
                            status=res.status_code,
                            template_name=res.template_name,
                            exception=res.exception,
                            content_type=res.content_type
                            )
        return res 
    def perform_update(self, serializer):
        # Check if the model instance has the 'updated_by' field
        if hasattr(serializer.instance, 'updated_by'):
            # Set 'updated_by' to the current user or null if the user is anonymous
            user = self.request.user
            serializer.save(updated_by=user if user.is_authenticated else None)
        else:
            serializer.save()
    def patch(self, request, *args, **kwargs):
        res=super().patch(request, *args, **kwargs)
        if res.status_code ==200:
            return Response({ "message": "Record Updated Successfully.", "data": res.data},
                            headers=res.headers,
                            status=res.status_code,
                            template_name=res.template_name,
                            exception=res.exception,
                            content_type=res.content_type
                            )
        return res 
    
    def delete(self, request, *args, **kwargs):
        res=super().delete(request, *args, **kwargs)
        if res.status_code ==status.HTTP_204_NO_CONTENT:
            return Response({ "message": "Record Delectd Successfully.", "data": res.data},
                            headers=res.headers,
                            status=res.status_code,
                            template_name=res.template_name,
                            exception=res.exception,
                            content_type=res.content_type
                            )
        return res 
    
    