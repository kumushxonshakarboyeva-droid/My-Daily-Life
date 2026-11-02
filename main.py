# -*- coding: utf-8 -*-
"""My Daily Life — Kivy Android app starter.

Offline-first personal planner. Data is stored as JSON in App.user_data_dir.
Build for Android with Buildozer (see buildozer.spec example in the chat).
"""
from __future__ import annotations

import json
import os
import time
from datetime import date, datetime, timedelta
from functools import partial

from kivy.app import App
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.utils import get_color_from_hex
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.uix.progressbar import ProgressBar
from kivy.uix.spinner import Spinner
from kivy.uix.widget import Widget

PINK = get_color_from_hex('#E88EAD')
DARK = get_color_from_hex('#553846')
PALE = get_color_from_hex('#FFF1F5')
WHITE = get_color_from_hex('#FFFFFF')
MUTED = get_color_from_hex('#927987')
GREEN = get_color_from_hex('#77A98B')

DEFAULT_CEFR = [
    'Grammar: kanal darsi + Murphy 2 unit',
    'Writing: 10–15 gap yozish va tekshirtirish',
    'Reading: 1 matn, tarjima va mashqlar',
    'Listening: video va 2–3 ta YouTube subtitr',
    'O‘qituvchidan berilgan Multilevel vazifasi',
    'Tactics for Listening: 1 unit',
]
DEFAULT_PRAYERS = ['Bomdod', 'Peshin', 'Asr', 'Shom', 'Xufton']
DEFAULT_HOME = ['Yotoqlarni yig‘ish', 'Idishlarni yuvish', 'Pol supurish', 'Hammomni tozalash', 'Kir yuvish', 'Oshxonani yig‘ishtirish']


def fresh_data():
    today = date.today().isoformat()
    tasks = []
    for title in DEFAULT_CEFR:
        tasks.append({'id': make_id(), 'title': title, 'section': 'CEFR', 'day': today,
                      'done': False, 'priority': 'O‘rta', 'repeat': 'Yo‘q', 'seconds': 0,
                      'timer_started': None})
    for title in DEFAULT_PRAYERS:
        tasks.append({'id': make_id(), 'title': title, 'section': 'Ibodat', 'day': today,
                      'done': False, 'priority': 'Yuqori', 'repeat': 'Kunlik', 'seconds': 0,
                      'timer_started': None})
    for title in DEFAULT_HOME:
        tasks.append({'id': make_id(), 'title': title, 'section': 'Uy ishlari', 'day': today,
                      'done': False, 'priority': 'O‘rta', 'repeat': 'Kunlik', 'seconds': 0,
                      'timer_started': None})
    return {
        'tasks': tasks, 'journal': [], 'words': [], 'writing': [], 'scores': [],
        'qazo': 0, 'dhikr': [], 'quran': [], 'recipes': [], 'children': [],
        'wishlist': [], 'weekly': [], 'settings': {'class_time': '19:10'},
        'created': datetime.now().isoformat(timespec='seconds')
    }


def make_id():
    return str(int(time.time() * 1000)) + str(os.getpid())


class MyDailyLife(App):
    title = 'My Daily Life'

    def build(self):
        Window.clearcolor = PALE
        self.data = self.load_data()
        self.current_section = 'Bosh sahifa'
        self.timer_event = Clock.schedule_interval(self.tick_timers, 1)
        self.root_box = BoxLayout(orientation='vertical', spacing=dp(7), padding=dp(10))
        self.header = Label(text='♡  My Daily Life  ♡', size_hint_y=None, height=dp(48),
                            color=DARK, bold=True, font_size='23sp')
        self.root_box.add_widget(self.header)
        self.content = BoxLayout(orientation='vertical')
        self.root_box.add_widget(self.content)
        self.show_dashboard()
        return self.root_box

    @property
    def data_path(self):
        return os.path.join(self.user_data_dir, 'my_daily_life.json')

    def load_data(self):
        try:
            with open(self.data_path, 'r', encoding='utf-8') as f:
                obj = json.load(f)
            base = fresh_data()
            base.update(obj if isinstance(obj, dict) else {})
            base.setdefault('tasks', [])
            return base
        except Exception:
            return fresh_data()

    def save_data(self, *_):
        os.makedirs(self.user_data_dir, exist_ok=True)
        tmp = self.data_path + '.tmp'
        with open(tmp, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)
        os.replace(tmp, self.data_path)

    def clear_content(self):
        self.content.clear_widgets()

    def make_button(self, text, callback, height=46, color=PINK):
        b = Button(text=text, size_hint_y=None, height=dp(height), background_normal='',
                   background_color=color, color=WHITE, bold=True)
        b.bind(on_release=callback)
        return b

    def make_label(self, text, size=15, height=None, color=DARK, bold=False):
        lbl = Label(text=text, size_hint_y=(None if height else 1),
                    height=dp(height) if height else None, color=color,
                    font_size=f'{size}sp', bold=bold, halign='left', valign='middle')
        lbl.bind(size=lambda inst, val: setattr(inst, 'text_size', (val[0], None)))
        return lbl

    def make_scroll(self):
        scroll = ScrollView(do_scroll_x=False)
        box = BoxLayout(orientation='vertical', spacing=dp(7), padding=dp(4), size_hint_y=None)
        box.bind(minimum_height=box.setter('height'))
        scroll.add_widget(box)
        return scroll, box

    def show_dashboard(self, *_):
        self.current_section = 'Bosh sahifa'
        self.clear_content()
        scroll, box = self.make_scroll()
        today = date.today().isoformat()
        today_tasks = [t for t in self.data['tasks'] if t.get('day') == today]
        done = sum(1 for t in today_tasks if t.get('done'))
        total = len(today_tasks)
        box.add_widget(self.make_label(f'Bugungi bajarilish: {done}/{total}', 18, 34, DARK, True))
        bar = ProgressBar(max=max(total, 1), value=done, size_hint_y=None, height=dp(14))
        box.add_widget(bar)
        next_task = next((t for t in today_tasks if not t.get('done')), None)
        box.add_widget(self.make_label('Keyingi vazifa: ' + (next_task['title'] if next_task else 'Bugungi vazifalar bajarildi 🎉'), 15, 48))
        sections = [
            ('CEFR', 'CEFR'), ('Ibodat', 'Ibodat'), ('Uy ishlari', 'Uy ishlari'),
            ('Bolalar', 'Bolalar'), ('Haftalik reja', 'Haftalik reja'),
            ('Statistika', 'Statistika'), ('Kunlik anglashlarim', 'Kundalik'),
            ('My Wishlist', 'Wishlist'), ('Sozlamalar / Backup', 'Sozlamalar')]
        grid = GridLayout(cols=2, spacing=dp(8), size_hint_y=None)
        grid.bind(minimum_height=grid.setter('height'))
        for title, section in sections:
            grid.add_widget(self.make_button(title, partial(self.open_section, section), 62))
        box.add_widget(grid)
        box.add_widget(self.make_button('Bugungi vazifalar', self.show_today_tasks, 48, GREEN))
        self.content.add_widget(scroll)

    def open_section(self, section, *_):
        self.current_section = section
        if section == 'CEFR': self.show_cefr()
        elif section == 'Ibodat': self.show_worship()
        elif section == 'Uy ishlari': self.show_tasks('Uy ishlari')
        elif section == 'Bolalar': self.show_children()
        elif section == 'Haftalik reja': self.show_weekly()
        elif section == 'Statistika': self.show_stats()
        elif section == 'Kundalik': self.show_journal()
        elif section == 'Wishlist': self.show_wishlist()
        elif section == 'Sozlamalar': self.show_settings()

    def section_page(self, title):
        self.clear_content()
        top = BoxLayout(size_hint_y=None, height=dp(42), spacing=dp(6))
        top.add_widget(self.make_button('← Orqaga', self.show_dashboard, 40, MUTED))
        top.add_widget(self.make_label(title, 18, 40, DARK, True))
        self.content.add_widget(top)
        scroll, box = self.make_scroll()
        self.content.add_widget(scroll)
        return box

    def show_today_tasks(self, *_):
        self.show_tasks(None)

    def show_tasks(self, section=None):
        title = section or 'Bugungi vazifalar'
        box = self.section_page(title)
        today = date.today().isoformat()
        tasks = [t for t in self.data['tasks'] if t.get('day') == today and (section is None or t.get('section') == section)]
        if not tasks:
            box.add_widget(self.make_label('Hozircha vazifa yo‘q.', 15, 40))
        for task in tasks:
            self.add_task_row(box, task)
        box.add_widget(self.make_button('+ Yangi vazifa qo‘shish', partial(self.add_task_popup, section or 'Umumiy')))
        box.add_widget(self.make_button('Bajarilmaganlarni ertaga ko‘chirish', partial(self.rollover_tasks, section), 48, GREEN))

    def add_task_row(self, box, task):
        row = BoxLayout(size_hint_y=None, height=dp(78), spacing=dp(5), padding=dp(4))
        row.add_widget(self.make_button('✓' if task.get('done') else '○', partial(self.toggle_task, task['id']), 54, GREEN if task.get('done') else MUTED))
        info = BoxLayout(orientation='vertical', spacing=dp(1))
        info.add_widget(self.make_label(task['title'], 14, 35, DARK, True))
        elapsed = self.task_elapsed(task)
        info.add_widget(self.make_label(f"{task.get('priority','O‘rta')}  •  Taymer: {elapsed//60:02d}:{elapsed%60:02d}", 11, 25, MUTED))
        row.add_widget(info)
        row.add_widget(self.make_button('▶/Ⅱ', partial(self.toggle_timer, task['id']), 54))
        row.add_widget(self.make_button('✎', partial(self.edit_task_popup, task['id']), 54, MUTED))
        box.add_widget(row)

    def toggle_task(self, task_id, *_):
        task = self.find_task(task_id)
        if task:
            task['done'] = not task.get('done', False)
            if task['done']: task['timer_started'] = None
            self.save_data()
            self.refresh_current()

    def find_task(self, task_id):
        return next((t for t in self.data['tasks'] if t.get('id') == task_id), None)

    def task_elapsed(self, task):
        secs = int(task.get('seconds', 0))
        if task.get('timer_started'):
            secs += max(0, int(time.time() - task['timer_started']))
        return secs

    def toggle_timer(self, task_id, *_):
        task = self.find_task(task_id)
        if not task: return
        if task.get('timer_started'):
            task['seconds'] = self.task_elapsed(task)
            task['timer_started'] = None
        elif not task.get('done'):
            task['timer_started'] = time.time()
        self.save_data()
        self.refresh_current()

    def tick_timers(self, _dt):
        # Persist active timer state periodically; timer remains accurate after app restart.
        if any(t.get('timer_started') for t in self.data.get('tasks', [])):
            self.save_data()

    def refresh_current(self):
        sec = self.current_section
        if sec == 'Bosh sahifa': self.show_dashboard()
        elif sec == 'CEFR': self.show_cefr()
        elif sec == 'Ibodat': self.show_worship()
        elif sec == 'Uy ishlari': self.show_tasks('Uy ishlari')
        elif sec == 'Bolalar': self.show_children()
        elif sec == 'Haftalik reja': self.show_weekly()
        elif sec == 'Statistika': self.show_stats()
        elif sec == 'Kundalik': self.show_journal()
        elif sec == 'Wishlist': self.show_wishlist()
        else: self.show_today_tasks()

    def add_task_popup(self, section='Umumiy', *_):
        self.task_form_popup(section)

    def edit_task_popup(self, task_id, *_):
        task = self.find_task(task_id)
        if task: self.task_form_popup(task.get('section', 'Umumiy'), task)

    def task_form_popup(self, section, task=None):
        form = BoxLayout(orientation='vertical', spacing=dp(8), padding=dp(10))
        title = TextInput(text=task.get('title','') if task else '', hint_text='Vazifa nomi', size_hint_y=None, height=dp(44), multiline=False)
        priority = Spinner(text=task.get('priority','O‘rta') if task else 'O‘rta', values=['Yuqori','O‘rta','Past'], size_hint_y=None, height=dp(44))
        repeat = Spinner(text=task.get('repeat','Yo‘q') if task else 'Yo‘q', values=['Yo‘q','Kunlik','Haftalik'], size_hint_y=None, height=dp(44))
        day = TextInput(text=task.get('day',date.today().isoformat()) if task else date.today().isoformat(), hint_text='Sana: YYYY-MM-DD', size_hint_y=None, height=dp(44), multiline=False)
        for w in (title, priority, repeat, day): form.add_widget(w)
        buttons = BoxLayout(size_hint_y=None, height=dp(45), spacing=dp(5))
        popup = Popup(title='Vazifa', content=form, size_hint=(.92,.62))
        def save(*_):
            if not title.text.strip(): return
            if task:
                task.update(title=title.text.strip(), priority=priority.text, repeat=repeat.text, day=day.text.strip())
            else:
                self.data['tasks'].append({'id':make_id(),'title':title.text.strip(),'section':section,'day':day.text.strip(),'done':False,'priority':priority.text,'repeat':repeat.text,'seconds':0,'timer_started':None})
            self.save_data(); popup.dismiss(); self.refresh_current()
        buttons.add_widget(self.make_button('Saqlash', save, 42, GREEN))
        buttons.add_widget(self.make_button('Bekor', popup.dismiss, 42, MUTED))
        form.add_widget(buttons); popup.open()

    def rollover_tasks(self, section=None, *_):
        tomorrow = (date.today()+timedelta(days=1)).isoformat()
        count = 0
        for task in self.data['tasks']:
            if task.get('day') == date.today().isoformat() and not task.get('done') and (section is None or task.get('section') == section):
                # High-priority fixed items are copied only after explicit user action.
                clone = dict(task); clone['id'] = make_id(); clone['day'] = tomorrow; clone['seconds'] = 0; clone['timer_started'] = None; clone['done'] = False
                self.data['tasks'].append(clone); count += 1
        self.save_data(); self.info_popup('Ko‘chirildi', f'{count} ta bajarilmagan vazifa ertangi kunga qo‘shildi.')
        self.refresh_current()

    def show_cefr(self):
        box = self.section_page('CEFR — 6 kunlik vazifa')
        box.add_widget(self.make_label('Jonli dars: 19:10 (Sozlamalarda o‘zgartirish mumkin)', 14, 34, MUTED))
        for task in self.data['tasks']:
            if task.get('section') == 'CEFR' and task.get('day') == date.today().isoformat(): self.add_task_row(box, task)
        box.add_widget(self.make_button('+ CEFR vazifasi', partial(self.add_task_popup,'CEFR')))
        box.add_widget(self.make_button('Writing javobini saqlash', self.writing_popup))
        box.add_widget(self.make_button('Yangi so‘z qo‘shish', self.word_popup))
        box.add_widget(self.make_button('So‘zlarni takrorlash (quiz)', self.vocab_quiz, 48, GREEN))
        box.add_widget(self.make_button('Reading / Listening natijasini kiritish', self.score_popup))
        box.add_widget(self.make_label('Saqlangan writinglar: '+str(len(self.data['writing']))+' | Lug‘at: '+str(len(self.data['words']))+' | Natijalar: '+str(len(self.data['scores'])), 13, 32, MUTED))

    def writing_popup(self, *_):
        self.text_record_popup('Writing javobi', 'writing', 'Mavzu va javobingizni yozing')

    def word_popup(self, *_):
        form = BoxLayout(orientation='vertical', spacing=dp(6), padding=dp(8))
        en = TextInput(hint_text='English word', size_hint_y=None, height=dp(42), multiline=False)
        uz = TextInput(hint_text='O‘zbekcha tarjima / misol', size_hint_y=None, height=dp(42), multiline=False)
        form.add_widget(en); form.add_widget(uz)
        pop = Popup(title='Lug‘at', content=form, size_hint=(.9,.45))
        def save(*_):
            if en.text.strip(): self.data['words'].append({'en':en.text.strip(),'uz':uz.text.strip(),'known':False}); self.save_data(); pop.dismiss(); self.show_cefr()
        form.add_widget(self.make_button('Saqlash', save)); pop.open()

    def vocab_quiz(self, *_):
        words = [w for w in self.data['words'] if not w.get('known')]
        if not words: self.info_popup('Lug‘at', 'Takrorlash uchun so‘z yo‘q. Avval so‘z qo‘shing.'); return
        w = words[0]
        pop = Popup(title='So‘zni eslang', content=Label(text=f"{w['en']}\n\nTarjimasini eslang: {w['uz']}", color=DARK), size_hint=(.85,.35))
        pop.open()
        pop.bind(on_dismiss=lambda *_: self.mark_word_known(w))

    def mark_word_known(self, word):
        word['known'] = True; self.save_data()

    def score_popup(self, *_):
        self.text_record_popup('Reading / Listening natijasi', 'scores', 'Bo‘lim, sana va ballni yozing')

    def text_record_popup(self, title, key, hint):
        form = BoxLayout(orientation='vertical', spacing=dp(7), padding=dp(8))
        inp = TextInput(hint_text=hint, multiline=True)
        form.add_widget(inp)
        pop = Popup(title=title, content=form, size_hint=(.92,.65))
        def save(*_):
            if inp.text.strip(): self.data[key].append({'date':date.today().isoformat(),'text':inp.text.strip()}); self.save_data(); pop.dismiss(); self.refresh_current()
        form.add_widget(self.make_button('Saqlash', save)); pop.open()

    def show_worship(self):
        box = self.section_page('Ibodat')
        today = date.today().isoformat()
        for prayer in DEFAULT_PRAYERS:
            key = f'{today}|{prayer}'
            done = any(x.get('key') == key for x in self.data.get('dhikr', []))
            box.add_widget(self.make_button(('✓ ' if done else '○ ')+prayer, partial(self.toggle_prayer, key), 46, GREEN if done else PINK))
        box.add_widget(self.make_label(f"Qazo namoz hisoblagichi: {self.data.get('qazo',0)}", 15, 34, DARK, True))
        controls = BoxLayout(size_hint_y=None, height=dp(45), spacing=dp(6))
        controls.add_widget(self.make_button('Qazo +1', partial(self.change_qazo,1), 42))
        controls.add_widget(self.make_button('Qazo −1', partial(self.change_qazo,-1), 42, MUTED))
        box.add_widget(controls)
        box.add_widget(self.make_button('Qur’on tilovati qaydi', partial(self.text_record_popup,'Qur’on jurnali','quran','Sura, oyat yoki o‘qilgan miqdor')))
        box.add_widget(self.make_button('Daloilul Xoyrot qaydi', partial(self.text_record_popup,'Daloilul Xoyrot','dhikr','Bugungi o‘qish qaydi')))
        box.add_widget(self.make_label('Namoz vaqtlari hozircha qo‘lda kiritiladigan eslatma sifatida ishlaydi; avtomatik vaqt manbasi ulanmagan.', 12, 52, MUTED))

    def toggle_prayer(self, key, *_):
        records = self.data.setdefault('dhikr', [])
        existing = next((x for x in records if x.get('key') == key), None)
        if existing: records.remove(existing)
        else: records.append({'key':key,'date':date.today().isoformat(),'type':'prayer'})
        self.save_data(); self.show_worship()

    def change_qazo(self, amount, *_):
        self.data['qazo'] = max(0, int(self.data.get('qazo',0))+amount); self.save_data(); self.show_worship()

    def show_children(self):
        box = self.section_page('Bolalar')
        box.add_widget(self.make_label('Har bir qaydni sana bilan saqlang: ovqat, uyqu, sayr, bo‘y-vazn, dori yoki mashg‘ulot.', 13, 52, MUTED))
        box.add_widget(self.make_button('+ Bola qaydi qo‘shish', self.child_popup))
        for item in reversed(self.data.get('children', [])[-30:]):
            box.add_widget(self.make_label(f"{item.get('date','')} • {item.get('child','')} • {item.get('kind','')}\n{item.get('note','')}", 13, 58))

    def child_popup(self, *_):
        form = BoxLayout(orientation='vertical', spacing=dp(6), padding=dp(8))
        child = Spinner(text='Katta farzand', values=['Katta farzand','Kichik farzand'], size_hint_y=None, height=dp(42))
        kind = Spinner(text='Ovqat', values=['Ovqat','Uyqu','Sayr','Yozuv mashqi','Bo‘y / vazn','Cho‘miltirish','Dori / shifokor','Boshqa'], size_hint_y=None, height=dp(42))
        note = TextInput(hint_text='Izoh, vaqt, miqdor...', multiline=True)
        for w in (child,kind,note): form.add_widget(w)
        pop = Popup(title='Bola qaydi', content=form, size_hint=(.92,.7))
        def save(*_):
            self.data['children'].append({'date':date.today().isoformat(),'child':child.text,'kind':kind.text,'note':note.text.strip()}); self.save_data(); pop.dismiss(); self.show_children()
        form.add_widget(self.make_button('Saqlash', save)); pop.open()

    def show_weekly(self):
        box = self.section_page('Haftalik reja')
        box.add_widget(self.make_button('+ Haftalik vazifa', partial(self.add_task_popup,'Haftalik reja')))
        today = date.today()
        start = today - timedelta(days=today.weekday())
        for i in range(7):
            d = start + timedelta(days=i)
            day_tasks = [t for t in self.data['tasks'] if t.get('day') == d.isoformat()]
            box.add_widget(self.make_label(f"{d.strftime('%A %d.%m')} — {sum(1 for t in day_tasks if t.get('done'))}/{len(day_tasks)} bajarildi", 14, 32, DARK, True))
            for t in day_tasks: self.add_task_row(box,t)
        box.add_widget(self.make_button('Bajarilmaganlarni ertaga ko‘chirish', self.rollover_tasks, 48, GREEN))

    def show_stats(self):
        box = self.section_page('Statistika')
        today = date.today()
        for label, days in [('Bugun',1),('7 kun',7),('30 kun',30)]:
            start = (today-timedelta(days=days-1)).isoformat()
            tasks = [t for t in self.data['tasks'] if start <= t.get('day','') <= today.isoformat()]
            done = sum(1 for t in tasks if t.get('done'))
            pct = round(done*100/len(tasks)) if tasks else 0
            box.add_widget(self.make_label(f'{label}: {done}/{len(tasks)} — {pct}%', 17, 42, DARK, True))
        by_section = {}
        for t in self.data['tasks']:
            key=t.get('section','Umumiy'); by_section.setdefault(key,[0,0]); by_section[key][1]+=1; by_section[key][0]+=int(bool(t.get('done')))
        for k,(d,n) in by_section.items(): box.add_widget(self.make_label(f'{k}: {d}/{n}',14,30))
        total_secs = sum(self.task_elapsed(t) for t in self.data['tasks'])
        box.add_widget(self.make_label(f'Vazifalarga sarflangan vaqt: {total_secs//3600} soat {(total_secs%3600)//60} daqiqa', 14, 40, MUTED))

    def show_journal(self):
        box = self.section_page('Kunlik anglashlarim')
        box.add_widget(self.make_button('+ Yangi yozuv', self.journal_popup))
        for item in reversed(self.data.get('journal', [])):
            row=BoxLayout(size_hint_y=None,height=dp(60),spacing=dp(5))
            row.add_widget(self.make_label(f"{item.get('date')} — {item.get('title')}\n{item.get('text','')[:90]}",13,58))
            row.add_widget(self.make_button('✎',partial(self.journal_popup,item),48,MUTED))
            row.add_widget(self.make_button('×',partial(self.delete_record,'journal',item),48,MUTED))
            box.add_widget(row)

    def journal_popup(self, item=None, *_):
        form=BoxLayout(orientation='vertical',spacing=dp(6),padding=dp(8))
        title=TextInput(text=item.get('title','') if item else '',hint_text='Sarlavha',size_hint_y=None,height=dp(42),multiline=False)
        body=TextInput(text=item.get('text','') if item else '',hint_text='Bugungi fikrlaringiz...',multiline=True)
        form.add_widget(title);form.add_widget(body)
        pop=Popup(title='Kundalik',content=form,size_hint=(.92,.72))
        def save(*_):
            if title.text.strip() or body.text.strip():
                if item: item.update(title=title.text.strip(),text=body.text.strip())
                else: self.data['journal'].append({'date':date.today().isoformat(),'title':title.text.strip(),'text':body.text.strip()})
                self.save_data();pop.dismiss();self.show_journal()
        form.add_widget(self.make_button('Saqlash',save));pop.open()

    def show_wishlist(self):
        box=self.section_page('My Wishlist')
        box.add_widget(self.make_button('+ Orzu / maqsad',self.wish_popup))
        for item in self.data.get('wishlist',[]):
            box.add_widget(self.make_button(('✓ ' if item.get('done') else '♡ ')+item.get('text',''),partial(self.toggle_wish,item),48,GREEN if item.get('done') else PINK))

    def wish_popup(self,*_):
        form=BoxLayout(orientation='vertical',spacing=dp(6),padding=dp(8))
        inp=TextInput(hint_text='Orzu, xarid yoki maqsad',multiline=True)
        form.add_widget(inp);pop=Popup(title='Wishlist',content=form,size_hint=(.9,.45))
        def save(*_):
            if inp.text.strip():self.data['wishlist'].append({'text':inp.text.strip(),'done':False});self.save_data();pop.dismiss();self.show_wishlist()
        form.add_widget(self.make_button('Saqlash',save));pop.open()

    def toggle_wish(self,item,*_):item['done']=not item.get('done');self.save_data();self.show_wishlist()

    def show_settings(self):
        box=self.section_page('Sozlamalar / Backup')
        box.add_widget(self.make_label('Dars vaqti',14,30,DARK,True))
        inp=TextInput(text=self.data.get('settings',{}).get('class_time','19:10'),hint_text='19:10',size_hint_y=None,height=dp(42),multiline=False)
        box.add_widget(inp)
        def save_time(*_):self.data.setdefault('settings',{})['class_time']=inp.text.strip();self.save_data();self.info_popup('Saqlandi','Dars vaqti saqlandi.')
        box.add_widget(self.make_button('Vaqtni saqlash',save_time))
        box.add_widget(self.make_button('JSON backup faylini yaratish',self.export_backup,48,GREEN))
        box.add_widget(self.make_button('Backup matnini tiklash',self.import_backup))
        box.add_widget(self.make_label('Ma’lumotlar telefonda saqlanadi. Google Cloud sinxronlash va Android fon bildirishnomalari hali ulanmagan. Backupni qo‘lda eksport/import qilish mumkin.',12,80,MUTED))

    def export_backup(self,*_):
        path=os.path.join(self.user_data_dir,'my_daily_life_backup.json')
        with open(path,'w',encoding='utf-8') as f:json.dump(self.data,f,ensure_ascii=False,indent=2)
        self.info_popup('Backup tayyor',f'Fayl saqlandi:\n{path}\nUni telefon fayllariga ulashish uchun Android share funksiyasi keyin ulanadi.')

    def import_backup(self,*_):
        form=BoxLayout(orientation='vertical',spacing=dp(6),padding=dp(8))
        inp=TextInput(hint_text='Backup JSON matnini shu yerga joylang',multiline=True)
        form.add_widget(inp);pop=Popup(title='Backup tiklash',content=form,size_hint=(.94,.75))
        def restore(*_):
            try:
                obj=json.loads(inp.text)
                if not isinstance(obj,dict) or 'tasks' not in obj:raise ValueError('Backup formati noto‘g‘ri')
                self.data=obj;self.save_data();pop.dismiss();self.show_dashboard();self.info_popup('Tayyor','Backup tiklandi.')
            except Exception as e:self.info_popup('Xatolik',str(e))
        form.add_widget(self.make_button('Tiklash',restore));pop.open()

    def delete_record(self,key,item,*_):
        if item in self.data.get(key,[]):self.data[key].remove(item);self.save_data();self.show_journal()

    def info_popup(self,title,message):
        pop=Popup(title=title,content=Label(text=message,color=DARK),size_hint=(.88,.35));pop.open()

    def on_pause(self):
        self.save_data();return True

    def on_stop(self):
        self.save_data()


if __name__ == '__main__':
    MyDailyLife().run()
