from .models import Category

# displays categories on navigation bar

def menu_links(request):
    links = Category.objects.all()
    return dict(links=links)