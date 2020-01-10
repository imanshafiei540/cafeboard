# -*- coding: utf-8 -*-
from django.shortcuts import render
from website.models import *
from django.http import JsonResponse, HttpResponse
from django.forms.models import model_to_dict
import requests
from bs4 import BeautifulSoup
from xlrd import open_workbook
import jdatetime, locale


def get_tabletop_games():
    boardgames_name = [
        'Camel Up',
        'Dice Forge',
        'Vikings on Board',
        'Pandemic: The Cure',
        'Sushi Go Party!',
        'Spring Meadow',
        'Azul',
        'Sagrada',
        'Santorini',
        'Imhotep'
    ]

    boardgames_data = []

    for bg in boardgames_name:
        bg_obj = Boardgame.objects.get(name=bg)
        boardgames_data.append({
            'name': bg_obj.name,
            'image': bg_obj.image.url
        })
    return boardgames_data


def index(request):
    jdatetime.set_locale('fa_IR')
    boardgames = Boardgame.objects.all()
    counts = boardgames.count()
    events = Event.objects.all()
    events_list = []
    dorna_events = EventDorna.objects.all()
    dorna_events_list = []
    for event in events:
        jalali_date = jdatetime.date.fromgregorian(date=event.datetime.date())
        name_day = jalali_date.strftime("%a")
        month_name = jalali_date.strftime("%b")
        events_list.append(
            {"date": {"day": name_day, "month_name": month_name, "jalali": jalali_date, "image": event.image.url},
             "event": event})

    for event in dorna_events:
        jalali_date = jdatetime.date.fromgregorian(date=event.datetime.date())
        name_day = jalali_date.strftime("%a")
        month_name = jalali_date.strftime("%b")
        dorna_events_list.append(
            {"date": {"day": name_day, "month_name": month_name, "jalali": jalali_date, "image": event.image.url},
             "event": event})

    leads_dict = []
    all_leads = LeaderBoard.objects.all()
    for lead in all_leads:
        ranks = PersonToLeaderBoard.objects.filter(leader_board=lead).order_by("rank")
        rank_data = []
        for rank in ranks:
            rank_data.append({
                "name": rank.person_name,
                "points": rank.points,
                "rank": rank.rank
            })
        lead_data = {
            "boardgame": lead.boardgame_name,
            "robot_number": lead.robot_number,
            "ranks": rank_data
        }
        leads_dict.append(lead_data)

    print(leads_dict)
    return render(request, 'index.html',
                  {'boardgames_count': counts, "events": events_list, "dorna_events": dorna_events_list,
                   "tabletop_games": get_tabletop_games(), "lead_data": leads_dict})


def getproducts(request):
    if request.method == "GET":
        boardgames = Boardgame.objects.filter(name__contains=request.GET['q'])
        data = {}
        bg_data = []
        bg_data_unique = []
        tags = []
        for boardgame in boardgames:
            for tag in Tag.objects.filter(boardgame=boardgame):
                tags.append(model_to_dict(tag))
            bg_data.append({'id': boardgame.pk, 'name': boardgame.name, 'image': boardgame.image.url,
                            'rate': int(boardgame.rate) * "★",
                            'tags': tags})
            tags = []

        boardgames_with_tag = Tag.objects.filter(name__contains=request.GET['q']).distinct()
        t_tags = []
        for boardgame_t in boardgames_with_tag:
            for tag in Tag.objects.filter(boardgame=boardgame_t.boardgame):
                t_tags.append(model_to_dict(tag))
            bg_data.append({'id': boardgame_t.boardgame.pk, 'name': boardgame_t.boardgame.name,
                            'image': boardgame_t.boardgame.image.url, 'rate': int(boardgame_t.boardgame.rate) * "★",
                            'tags': t_tags})
            t_tags = []

        for item in bg_data:
            if item not in bg_data_unique:
                bg_data_unique.append(item)
        data['boardgames'] = bg_data_unique
        return JsonResponse(data)


def getallboardgames(request):
    boardgames = Boardgame.objects.all()
    data = {}
    bg_data = []
    tags = []
    for boardgame in boardgames:
        for tag in Tag.objects.filter(boardgame=boardgame):
            tags.append(model_to_dict(tag))
        bg_data.append({'name': boardgame.name, 'image': boardgame.image.url, 'rate': int(boardgame.rate) * "★",
                        'tags': tags})
        tags = []

    data['boardgames'] = bg_data
    return JsonResponse(data)


def enter_bg_data(request):
    wb = open_workbook('/Users/impala69/Desktop/final.xlsx')
    for sheet in wb.sheets():
        number_of_rows = sheet.nrows
        for row in range(1, number_of_rows):
            tags = []
            bgg_code = int(sheet.cell(row, 1).value)
            category = sheet.cell(row, 4).value
            learning = sheet.cell(row, 8).value
            main_g = sheet.cell(row, 10).value
            sec_g = sheet.cell(row, 11).value
            if not category:
                category = "Light Strategy"
            if main_g:
                tags.append(main_g)
            if sec_g:
                tags.append(sec_g)

            print("bgg_code" + ": " + str(bgg_code))

            if bgg_code != 0:
                try:
                    url = "https://boardgamegeek.com/boardgame/" + str(bgg_code)
                    bgg_site_content = requests.get(url).content
                    soup = BeautifulSoup(bgg_site_content, 'html.parser')
                    game_content = soup.find("script")
                    game_data = game_content.text[
                                game_content.text.find("GEEK.geekitemPreload"):game_content.text.find(
                                    "GEEK.geekitemSettings") - 3]
                    game_data = game_data.replace("GEEK.geekitemPreload = ", "")
                    game_data = game_data.replace("true", "True")
                    game_data = game_data.replace("false", "False")
                    game_data = game_data.replace("null", "'null'")
                    game_json_data = eval(game_data)
                    min_player = int(game_json_data['item']['minplayers'])
                    max_player = int(game_json_data['item']['maxplayers'])
                    max_play_time = int(game_json_data['item']['maxplaytime'])
                    min_play_time = game_json_data['item']['minplaytime']
                    bg_name = game_json_data['item']['name']
                    min_best_player = game_json_data['item']['polls']['userplayers']['best'][0]['min']
                    max_best_player = int(game_json_data['item']['polls']['userplayers']['best'][0]['max'])
                    rank_point = game_json_data['item']['rankinfo'][0]['baverage']
                    description = game_json_data['item']['description']
                    image_url = game_json_data['item']['imageurl'].replace("\\", "/")
                    image_url = image_url.replace("//", "/")
                    image_url = image_url.replace("https", "http")
                    print("bg_name" + ": " + str(bg_name))
                    filename = bg_name.replace(" ", "") + ".jpg"
                    r = requests.get(image_url, timeout=10)
                    if r.status_code == 200:
                        with open("/Users/impala69/PycharmProjects/cafeboard/public/media/" + filename, 'wb') as f:
                            f.write(r.content)

                    category_object = Category.objects.get(name=category)
                    new_bg = Boardgame(name=bg_name, category=category_object, min_players=min_player,
                                       max_players=max_player, best_players=max_best_player, rate=rank_point,
                                       learning_time=learning, duration=max_play_time, image="./" + filename,
                                       description=description, bgg_code=bgg_code)
                    new_bg.save()

                    if max_play_time <= 15:
                        time_tag = "یک ربع"
                    elif max_play_time <= 30:
                        time_tag = "نیم ساعت"
                    elif max_play_time <= 60:
                        time_tag = "یک ساعت"
                    elif max_play_time <= 90:
                        time_tag = "یک ساعت و نیم"
                    elif max_play_time <= 120:
                        time_tag = "دو ساعت"
                    elif max_play_time <= 180:
                        time_tag = "سه ساعت"
                    elif max_play_time > 180:
                        time_tag = "بیشتر از سه ساعت"
                    else:
                        time_tag = "No Time"

                    tags.append(time_tag)

                    if category == "Heavy Strategy":
                        audience_tag = "برای خوره‌ها"
                    elif max_best_player == 2:
                        audience_tag = "برای زوج‌ها"
                    elif category == "Family & Party":
                        audience_tag = "برای خانواده‌ها"
                    elif max_player > 4:
                        audience_tag = "برای جمع‌ها"
                    else:
                        audience_tag = 'تفننی'

                    tags.append(audience_tag)

                    for tag in tags:
                        new_tag = Tag(name=tag, boardgame=new_bg)
                        new_tag.save()
                except Exception as e:
                    print("Errorrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrr: " + bg_name)
                    print(e)

        break


def add_boardgame(request):
    # http://127.0.0.1:8001/addboardgame?bgg_code=121921&category=Heavy%20Strategy&learning=60&main_g=Thematic&sec_g=
    if request.GET:
        tags = []
        bgg_code = request.GET['bgg_code']
        category = request.GET['category']
        learning = request.GET['learning']
        if category == "Family and Party":
            category = "Family & Party"
        if request.GET['main_g']:
            tags.append(request.GET['main_g'])
        if request.GET['sec_g']:
            tags.append(request.GET['sec_g'])

        try:
            url = "https://boardgamegeek.com/boardgame/" + str(bgg_code)
            bgg_site_content = requests.get(url).content
            soup = BeautifulSoup(bgg_site_content, 'html.parser')
            game_content = soup.find("script")
            game_data = game_content.text[
                        game_content.text.find("GEEK.geekitemPreload"):game_content.text.find(
                            "GEEK.geekitemSettings") - 3]
            game_data = game_data.replace("GEEK.geekitemPreload = ", "")
            game_data = game_data.replace("true", "True")
            game_data = game_data.replace("false", "False")
            game_data = game_data.replace("null", "'null'")
            game_json_data = eval(game_data)
            bg_name = game_json_data['item']['primaryname']['name']
            min_player = int(game_json_data['item']['minplayers'])
            max_player = int(game_json_data['item']['maxplayers'])
            max_play_time = int(game_json_data['item']['maxplaytime'])
            min_play_time = game_json_data['item']['minplaytime']
            bg_name = game_json_data['item']['name']
            if game_json_data['item']['polls']['userplayers']['best']:
                min_best_player = game_json_data['item']['polls']['userplayers']['best'][0]['min']
                max_best_player = int(game_json_data['item']['polls']['userplayers']['best'][0]['max'])
            else:
                min_best_player = 0
                max_best_player = 0
            rank_point = game_json_data['item']['rankinfo'][0]['baverage']
            description = game_json_data['item']['description']
            image_url = game_json_data['item']['imageurl'].replace("\\", "/")
            image_url = image_url.replace("//", "/")
            image_url = image_url.replace("https", "http")
            print("bg_name" + ": " + str(bg_name))
            filename = bg_name.replace(" ", "") + ".jpg"
            r = requests.get(image_url, timeout=10)
            if r.status_code == 200:
                with open("/Users/impala69/PycharmProjects/cafeboard/public/media/" + filename, 'wb') as f:
                    f.write(r.content)

            category_object = Category.objects.get(name=category)
            new_bg = Boardgame(name=bg_name, category=category_object, min_players=min_player,
                               max_players=max_player, best_players=max_best_player, rate=rank_point,
                               learning_time=learning, duration=max_play_time, image="./" + filename,
                               description=description, bgg_code=bgg_code)
            new_bg.save()

            if max_play_time <= 15:
                time_tag = "یک ربع"
            elif max_play_time <= 30:
                time_tag = "نیم ساعت"
            elif max_play_time <= 60:
                time_tag = "یک ساعت"
            elif max_play_time <= 90:
                time_tag = "یک ساعت و نیم"
            elif max_play_time <= 120:
                time_tag = "دو ساعت"
            elif max_play_time <= 180:
                time_tag = "سه ساعت"
            elif max_play_time > 180:
                time_tag = "بیشتر از سه ساعت"
            else:
                time_tag = "No Time"

            tags.append(time_tag)

            if category == "Heavy Strategy":
                audience_tag = "برای خوره‌ها"
            elif max_best_player == 2:
                audience_tag = "برای زوج‌ها"
            elif category == "Family & Party":
                audience_tag = "برای خانواده‌ها"
            elif max_player > 4:
                audience_tag = "برای جمع‌ها"
            else:
                audience_tag = 'تفننی'

            tags.append(audience_tag)

            for tag in tags:
                new_tag = Tag(name=tag, boardgame=new_bg)
                new_tag.save()
            return HttpResponse("SUCCESS: " + str(bgg_code))
        except Exception as e:
            print("Errorrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrr: " + bgg_code)
            print(e)
            return HttpResponse("Failed: " + str(bgg_code))


def get_bg_ctaegory(request):
    if request.method == "GET":
        cat = request.GET['cat']
        if cat == "Party":
            cat = "Family & Party"
        cat_obj = Category.objects.get(name=cat)
        print(cat_obj)
        bgs = Boardgame.objects.filter(category=cat_obj)
        bg_data = []
        bg_tags = []
        data = {}
        for bg in bgs:
            for tag in Tag.objects.filter(boardgame=bg):
                bg_tags.append(model_to_dict(tag))
            bg_data.append({'id': bg.pk, 'name': bg.name, 'image': bg.image.url,
                            'rate': int(bg.rate) * "★",
                            'tags': bg_tags})
            bg_tags = []

        data['boardgames'] = bg_data
        return JsonResponse(data)
