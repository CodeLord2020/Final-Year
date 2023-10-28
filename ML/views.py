from django.shortcuts import render, redirect
from .Textblob_sentiment import start_sentiment_analysis_TextBlob
from .Bert1_sentiment import start_sentiment_analysis_BERT1
from .VADER_sentiments import start_sentiment_analysis_VADER
from .Distilledbert import start_sentiment_analysis_distilbert
from django.contrib.auth.decorators import login_required
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.contrib import messages
from django.conf import settings

def landing(request):
    return render (request, 'templ/landing.html')

@login_required(login_url='login')
def home(request):
    
    if request.method == 'POST':
        keyword = request.POST.get('keyword')
        analysis_method = request.POST.get('analysis_method')

        # Redirect to the corresponding method view based on the selected_method
        if analysis_method == 'method1':
            return redirect('textblob_view', keyword=keyword)
        elif analysis_method == 'method2':
            return redirect('vader_view', keyword=keyword)
        elif analysis_method == 'method3':
            return redirect('bert1_view', keyword=keyword)
        elif analysis_method == 'method4':
            return redirect('distilledberta_view', keyword=keyword)

    return render (request, 'templ/index.html')

# @cache_page(60 * 30)
@login_required(login_url='login')
def textblob_view(request, keyword):
    sentiments_data, comments_wordcloud = start_sentiment_analysis_TextBlob(keyword)
    
    if sentiments_data is not None:
        avg_sentiment_score, img_str1, img_str2, top_pos_comments, top_neg_comments = sentiments_data

        context = {
            'keyword': keyword,
            'analysis_method': 'TextBlob',
            'chart1type': 'dist',
            'avg_sentiment_score': avg_sentiment_score,
            'hist_chart_filename': img_str1,
            'sentiments_chart_heatmap': img_str2,
            'top_neg_comments': top_neg_comments,
            'top_pos_comments': top_pos_comments,
            'comments_wordcloud': comments_wordcloud,
        }
    else:
        context = {
            'keyword': keyword,
            'analysis_method': 'TextBlob',
            'chart1type': '',
            'avg_sentiment_score': '',
            'hist_chart_filename': '',
            'sentiments_chart_heatmap': '',
            'top_pos_comments': '',
            'top_neg_comments': '',
            'comments_wordcloud': '',
        }

    return render(request, 'templ/result_page.html', context)

@login_required(login_url='login')
def vader_view(request, keyword):
    sentiments_data, comments_wordcloud = start_sentiment_analysis_VADER(keyword)
    
    if sentiments_data is not None:
        avg_sentiment_score, img_str1, img_str2, top_pos_comments, top_neg_comments = sentiments_data

        context = {
            'keyword': keyword,
            'analysis_method': 'VADER',
            'chart1type': 'dist',
            'avg_sentiment_score': avg_sentiment_score,
            'hist_chart_filename': img_str1,
            'sentiments_chart_heatmap': img_str2,
            'top_neg_comments': top_neg_comments,
            'top_pos_comments': top_pos_comments,
            'comments_wordcloud': comments_wordcloud,
        }
    else:
        context = {
            'keyword': keyword,
            'analysis_method': 'VADER',
            'chart1type': '',
            'avg_sentiment_score': '',
            'hist_chart_filename': '',
            'sentiments_chart_heatmap': '',
            'top_pos_comments': '',
            'top_neg_comments': '',
            'comments_wordcloud': '',
        }

    return render(request, 'templ/result_page.html', context)

@login_required(login_url='login')
def bert1_view(request, keyword):
    average_score,five_star_comments,one_star_comments,sentiments_bert_plot, piechart,  comments_wordcloud = start_sentiment_analysis_BERT1(keyword)
    
    if sentiments_bert_plot is not None:
        context = {
            'keyword': keyword,
            'analysis_method': 'BERT',
            'chart1type': 'bar',
            'avg_sentiment_score':average_score,
            'top_neg_comments': one_star_comments,
            'top_pos_comments': five_star_comments,
            'hist_chart_filename': sentiments_bert_plot,
            'sentiments_chart_heatmap': piechart,
            'comments_wordcloud': comments_wordcloud,
        }
    else:
        context = {
            
            'keyword': keyword,
            'analysis_method': 'BERT',
            'chart1type': '',
            'avg_sentiment_score':'',
            'top_neg_comments': '',
            'top_pos_comments': '',
            'hist_chart_filename': '',
            'sentiments_chart_heatmap': '',
            'comments_wordcloud': '',
        }

    return render(request, 'templ/result_page.html', context)


@login_required(login_url='login')
def distilledberta_view(request, keyword):
    average_score, positive_comments, negative_comments, sentiments_distilbert_plot, piechart, comments_wordcloud = start_sentiment_analysis_distilbert(keyword)
    
    if positive_comments is not None:
        context = {
            'keyword': keyword,
            'chart1type': 'bar',
            'analysis_method': 'DISTILLBERT',
            'top_neg_comments': negative_comments,
            'top_pos_comments': positive_comments,
            'avg_sentiment_score':average_score,
            'hist_chart_filename': sentiments_distilbert_plot,
            'sentiments_chart_heatmap': piechart,
            'comments_wordcloud': comments_wordcloud,
        }
    else:
        context = {
            
            'keyword': keyword,
            'analysis_method': 'RoBERTa1',
            'chart1type': '',
            'avg_sentiment_score':'',
            'hist_chart_filename': '',
            'top_pos_comments': '',
            'top_neg_comments': '',
            'sentiments_chart_heatmap': '',
            'comments_wordcloud': '',
        }

    return render(request, 'templ/result_page.html', context)



@login_required(login_url='login')
def contact(request):
    if request.method == 'POST':
        subject = request.POST.get('topic')
        message = request.POST.get('message')
        user_email = request.user.email
        username = request.user.username
        email_from = settings.EMAIL_HOST_USER
        email_to = settings.EMAIL_CONTACT

        try:
            # Send the email
            send_mail(
                'New Message from {}'.format(username),
                '',  # Leave the body empty, as we'll use the HTML template
                email_from,
                [email_to],
                html_message=render_to_string('auth/contact_email.html', {
                    'subject': subject,
                    'message': message,
                    'username': username,
                    'user_email': user_email,
                })
            )

            messages.success(request, 'Message sent successfully')
        except Exception as e:
            messages.error(request, f'Failed to send message. Error: {e}')

        return render(request, 'templ/contact.html')

    return render(request, 'templ/contact.html')