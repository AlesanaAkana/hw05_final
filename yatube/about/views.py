from django.views.generic.base import TemplateView


class AboutAuthorView(TemplateView):
    template_name = 'about/author.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['just_title'] = 'Об авторе'
        context['just_text'] = ('Здесь что-то рассказывается, '
                                'об авторе.')
        return context


class AboutTechView(TemplateView):
    template_name = 'about/tech.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['just_title'] = 'Технологии'
        context['just_text'] = ('Здесь может быть что-то интересное, '
                                'возможно так и есть.')
        return context
