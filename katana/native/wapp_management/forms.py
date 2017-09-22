from django import forms


class UploadFileForm(forms.Form):
    docfile = forms.FileField()