from django.shortcuts import render, redirect
from .forms import UploadForm
from .models import UploadedFile


def index(request):
    if request.method == "POST":
        form = UploadForm(request.POST, request.FILES)

        if form.is_valid():
            form.save()
            return redirect("index")
    else:
        form = UploadForm()

    files = UploadedFile.objects.all().order_by("-uploaded_at")

    return render(
        request,
        "uploads/index.html",
        {
            "form": form,
            "files": files,
        },
    )
