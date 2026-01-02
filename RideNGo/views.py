from django.shortcuts import render
 
def home(request):
    return render(request, 'home.html')
    
def base(request):
    return render(request, 'base.html')

def pictures(request):
    return render(request, 'pictures.html')

def footer(request):
    return render(request, 'footer.html')

