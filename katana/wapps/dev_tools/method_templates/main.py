    def MethodName(self, request):
        obj = json.loads(request.POST.get('data'))
        return { 'data' : obj }
