from django.forms import ModelForm

from .models import Comment, Post


class PostForm(ModelForm):
    class Meta:
        model = Post
        fields = ['text', 'group', 'image']
        required = {
            'text': True,
            'group': False,
            'image': False,
        }
        help_texts = {
            'text': 'Введите ваш текст в данное поле',
            'group': ('Здесь, по желанию, вы можете указать'
                      'группу, в которую вы хотите отправить вашу запись'),
            'image': 'Здесь вы можете прикрепить изображение'
        }


class CommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = ['text']
        required = {'text': True}
