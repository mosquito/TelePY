#-*- coding: utf-8 -*-
from django.db.models import *
from datetime import time, datetime
from timezones import TIME_ZONES
from random import randint, choice
import string


class Cdr(Model):
    DISPOSITIONS=(
        ('ANSWERED','Отвечен'),
        ('FAILED', 'Ошибка'),
        ('NO ANSWER','Нет ответа'),
        ('BUSY','Занято'),
        ('DOCUMENTATION','Документировано'),
        ('BILL','Биллинг'),
        ('IGNORE','Игнорировано'),
    )
    AMAFLAGS=(
        (1,'Не обсчитывать'),
        (2,'Обсчитывать'),
        (3,'По умолчанию (Документировать)'),
    )
    clid = CharField(max_length=80, editable=True, default='', null=False, verbose_name=u'имя CallerID', db_index=True)
    src = CharField(max_length=80, editable=True, default='', null=False, verbose_name=u'номер CallerID', db_index=True)
    dst = CharField(max_length=80, editable=True, default='', null=False, verbose_name=u'назначение', db_index=True)
    dcontext = ForeignKey("Contexts", blank=False, null=False, verbose_name='контекст', db_index=True, db_column='dcontext')
    channel = CharField(max_length=80, editable=True, default='', null=False, verbose_name=u'канал источника')
    dstchannel = CharField(max_length=80, editable=True, default='', null=False, verbose_name=u'канал назначения')
    lastapp = CharField(max_length=80, editable=True, default='', null=False, verbose_name=u'последнее приложение')
    lastdata = CharField(max_length=80, editable=True, default='', null=False, verbose_name=u'последнее значение')
    start = DateTimeField(editable=True, blank=False, auto_now_add=True, auto_now=False, null=False, verbose_name=u'начало вызова', db_index=True)
    answer = DateTimeField(editable=True, blank=False, auto_now_add=True, auto_now=False, null=False, verbose_name=u'начало разговора', db_index=True)
    end = DateTimeField(editable=True, blank=False, auto_now_add=True, auto_now=False, null=False, verbose_name=u'конец разговора', db_index=True)
    duration = PositiveIntegerField(editable=True, default=0, null=False, verbose_name=u'длительность разговора', db_index=True)
    billsec = PositiveIntegerField(editable=True, default=0, null=False, verbose_name=u'длительность разговора для учета', db_index=True)
    disposition = CharField(max_length=45, editable=True, default='', null=False, verbose_name=u'статус', choices=DISPOSITIONS, db_index=True)
    amaflags = PositiveIntegerField(editable=True, default=0, null=False, verbose_name=u'флаги для биллинга', choices=AMAFLAGS, db_index=True)
    accountcode = ForeignKey('address.Unit', blank=True, null=True, verbose_name='плательщик', db_index=True, db_column='accountcode')
    uniqueid = CharField(max_length=128, editable=True, default='', null=False, verbose_name=u'идентификатор канала', db_index=True)
    userfield = CharField(max_length=255, editable=True, default='', null=False, verbose_name=u'поле пользователя')
    callrecord = FileField(upload_to='/mnt/records', editable=False, blank=True, null=True, verbose_name='запись разговора')

    def __unicode__(self, *args, **kwargs):
        return u'%s | %s --> %s длит.: %s сек.' % (self.start, self.src, self.dst, self.billsec)


    class Meta:
        ordering = ['-start', 'src', 'disposition']
        unique_together = (('uniqueid',) , ('src', 'dst', 'start',))
        verbose_name = 'звонок'
        verbose_name_plural = 'звонки'

class Contexts(Model):
    IN_OUT = ((True, 'Входящий'), (False, 'Исходящий'), )
    name = CharField(max_length=15, primary_key=True,  blank=False, null=False, verbose_name='контекст', editable=True)
    full_name = CharField(max_length=15, blank=False, null=False, verbose_name='описание', editable=True)
    incoming = BooleanField(default=False, null=False, blank=False, verbose_name='Входящий', choices=IN_OUT, db_index=True)

    def __unicode__(self, *args, **kwargs):
        return u'%s' % (self.full_name)

    class Meta:
        ordering = ['name', ]
        verbose_name = 'контекст'
        verbose_name_plural = 'контексты'

class Extensions(Model):
    COMMENTED=(
        (1,'Нет'),
        (0,'Да')
    )
    APPS=(
        ("Dial", u"(Dial) Набрать номер"),
        ("HangUp", u"(HangUp) Положить трубку"),
        ("Wait", u"(Wait) Подождать x секунд"),
        ("Answer", u"(Answer) Поднять трубку"),
        ("AddQueueMember", u"AddQueueMember(queue,channel) Удалить из группы"),
        ("Queue", u"Queue (queue_name) Перейти в очередь"),
        ("PlayBack", u"(PlayBack) Проиграть звуковой файл"),
        ("Set", u"(Set) Установить переменную"),
        ("Read", u"(Read) Прочитать клав в перемен."),
        ("BackGround", u"(BackGround) Играть звук и ждать exten"),
        ("Bridge", u"(Bridge) Сделать мост 2х каналов"),
        ("Busy", u"(Busy) Вернуть \"занято\""),
        ("ChangeMonitor", u"(ChangeMonitor) Изм. файл канала монитора"),
        ("Congestion", u"(Congestion) Перегружено направление"),
        ("DBdel", u"(DBdel) Удалить ключ из внутр. БД"),
        ("DBdeltree", u"(DBdeltree) Удалить дерево из вн. БД"),
        ("Echo", u"(Echo) Проигрывать слышимое"),
        ("ConfBridge", u"(ConfBridge) Создать мост конференции"),
        ("Exec", u"(Exec) Выполнить прил. диалплана"),
        ("ExecIf", u"(ExecIf) Выполнить если"),
        ("ExecIfTime", u"(ExecIfTime) Выполнить если+время"),
        ("GoSub", u"GoSub([[context|]extension|]priority) Перейти в экстеншн после чего вернуться"),
        ("GoTo", u"GoTo([[context|]extension|]priority) Перейти в экстеншн"),
        ("GoToIf", u"GoToIf(condition?context1,extension1,priority1:context2,extension2,priority2)"),
        ("GotoIfTime", u"(GotoIfTime) Перейти экст. если+время"),
        ("ImportVar", u"(ImportVar) Импорт переменной в новую"),
        ("Incomplete", u"(Incomplete) Возвр. невыполненные"),
        ("Macro", u"(Macro) Выполнить макрос"),
        ("MacroExclusive", u"(MacroExclusive) Выпол. только один макрос"),
        ("MacroIf", u"(MacroIf) Макрос если"),
        ("Monitor", u"(Monitor) Мониторинг канала"),
        ("StopMonitor", u"(StopMonitor) Остановить мониторинг канала"),
        ("MSet", u"(MSet) Уст. переменные канала"),
        ("MusicOnHold", u"(MusicOnHold) Играть музыку ожидания"),
        ("NoCDR", u"(NoCDR) Не записывать CDR"),
        ("NoOp", u"(NoOp) Ничего не делать"),
        ("Park", u"(Park) Парковать"),
        ("MeetMeChannelAdmin", u"(MeetMeChannelAdmin) Администрирование канала"),
        ("ParkedCall", u"(ParkedCall) Ответить на паркованый"),
        ("PauseMonitor", u"(PauseMonitor) Приостановить монитор"),
        ("Proceeding", u"(Proceeding) Вызов совершается"),
        ("Progress", u"(Progress) Вызов в процессе"),
        ("RaiseException", u"(RaiseException) Вызвать исключение"),
        ("ReadExten", u"(ReadExten) Прочитать номер из перем."),
        ("ReadFile", u"(ReadFile) Проч. файл в перм. канала"),
        ("MeetMeAdmin", u"(MeetMeAdmin) Администрирование комнаты"),
        ("Record", u"(Record) Записать файл"),
        ("ResetCDR", u"(ResetCDR) Сбросить CDR"),
        ("RetryDial", u"(RetryDial) Повтор набора при неудаче"),
        ("RemoveQueueMember", u"RemoveQueueMember(queue,channel) Добавить в группу"),
        ("Ringing", u"(Ringing) Звонит телефон"),
        ("SayAlpha", u"(SayAlpha) Сказать Alpha"),
        ("SayDigits", u"(SayDigits) Говорить цифры"),
        ("SayNumber", u"(SayNumber) Говорить номер"),
        ("SayPhonetic", u"(SayPhonetic) Говорить фонетически"),
        ("SendFAX", u"(SendFAX) Передать факс"),
        ("ReceiveFAX", u"(ReceiveFAX) Принять факс"),
        ("SetAMAFlags", u"(SetAMAFlags) Установить AMA флаг"),
        ("SetCallerPres", u"(SetCallerPres) Установить показ callerID"),
        ("SetMusicOnHold", u"(SetMusicOnHold) Установить муз. ожидания"),
        ("SIPAddHeader", u"(SIPAddHeader) Доб. исх. заг. sip пакета"),
        ("SIPDtmfMode", u"(SIPDtmfMode) Изменить DTMF Mode"),
        ("SIPRemoveHeader", u"(SIPRemoveHeader) Уд. исх. заг. sip пакета"),
        ("StartMusicOnHold", u"(StartMusicOnHold) Начать проигрывать MOH"),
        ("MeetMeCount", u"(MeetMeCount) Счетчик"),
        ("Transfer", u"(Transfer) Перевод вызова на номер"),
        ("TryExec", u"(TryExec) Попробовать выполнить"),
        ("TrySystem", u"(TrySystem) Попробовать выполн. UNIX"),
        ("System", u"(System) Выполнить UNIX комманду"),
        ("UnpauseMonitor", u"(UnpauseMonitor) Снять монитор с паузы"),
        ("WaitExten", u"(WaitExten) Ждать добавочного"),
        ("WaitMusicOnHold", u"(WaitMusicOnHold) Ждать добав. играя MOH"),
        ("MeetMe", u"(MeetMe) Приложение конференций"),
        ("SLAStation", u"(SLAStation) Run Shared Line"),
        ("SLATrunk", u"(SLATrunk) Shared Line Appearance"),
    )
    commented = SmallIntegerField(default=0, null=False, blank=False, verbose_name='включен', choices=COMMENTED, db_index=True)
    context = ForeignKey(Contexts, blank=False, null=False, verbose_name='контекст', db_index=True, db_column='context')
    exten = CharField(max_length=80, blank=False, null=False, verbose_name='экстен/шаблон', db_index=True, db_column='exten')
    priority = IntegerField(null=False, blank=False, verbose_name='приоритет',)
    app = CharField(max_length=80, blank=False, null=False, verbose_name='приложение диалплана', db_index=True, db_column='app', choices=APPS)
    appdata = CharField(max_length=200, blank=True, null=True, verbose_name='параметры приложения', editable=True, db_index=True)

    class Meta:
        ordering = ['context__name', 'exten', 'priority']
        unique_together = (('context', 'exten', 'priority',) ,)
        verbose_name = 'экстеншн'
        verbose_name_plural = 'экстеншны'

    def __unicode__(self, *args, **kwargs):
        return u"%s| exten => %s,%s,%s(%s)" % (self.context, self.exten, self.priority, self.app, self.appdata)

class Numbers(Model):
    YESNO=(
        ('yes','Разрешить'),
        ('no', 'Запретить'),
    )
    TRUEFALSE=(
        (False,'Нет'),
        (True,'Да')
    )
    COMMENTED=(
        (1,'Нет'),
        (0,'Да')
    )
    TYPES=(
        ('peer','Только исходящие (peer)'),
        ('user','Только входящие (user)'),
        ('friend','Входящие и исходящие (friend)')
    )
    AMAFLAGS=(
        ('omit','Не обсчитывать (1)'),
        ('billing','Обсчитывать (2)'),
        ('default','По умолчанию (3)'),
        ('documentation','Документировать (3)'),
    )
    DTMFS=(
        ('inband','В потоке звука'),
        ('rfc2833','RFC2833'),
        ('info','SIP info DTMF'),
        ('auto','Автоопределение'),
    )
    INVITE=(
        ('port', "Игнорировать номер порта, с которого пришла аутентификация"),
        ('invite', "Не требовать начальное сообщение INVITE для аутентификации"),
        ("port,invite", """Не требовать начальное сообщение INVITE для аутентификации и игнорировать порт, с которого пришел запрос"""),
    )
    commented = SmallIntegerField(default=0, verbose_name='включен', choices=COMMENTED, db_index=True)
    name = CharField(max_length=15, verbose_name='номер', primary_key=True)
    host = CharField(max_length=25, verbose_name='хост', default='dynamic', help_text='привязка к определенному хосту или IP, или \'dynamic\'')
    nat = CharField(max_length=5, default='no', editable=True, verbose_name='NAT', help_text='разрешать ли работу через NAT', choices=YESNO)
    type = CharField(max_length=8, default='friend', editable=True, verbose_name='тип', help_text='тип пользователя', choices=TYPES)
    accountcode = ForeignKey('address.Unit', blank=True, null=True, verbose_name='принадлежит', db_column='accountcode')
    amaflags = CharField(max_length=20, default='billing', blank=False, null=False, editable=True, verbose_name='флаги биллинга', help_text='специальные флаги для управления обсчетом по умолчанию', choices=AMAFLAGS)
    callgroup = CharField(max_length=25, blank=True, null=True, editable=False, help_text='не используется, для совместимости')
    callerid = CharField(max_length=250, blank=True, null=True, editable=True, help_text='Оставить пустым для автоподстановки')
    cancallforward = CharField(max_length=3, default='yes', blank=False, null=False, editable=True, verbose_name='Перевод звонков', help_text='разрешать ли перевод звонков', choices=YESNO)
    directmedia = CharField(max_length=3, default='no', editable=True, verbose_name='Прямой поток', help_text='разрешать ли прямое прохождение трафика', choices=YESNO)
    context = ForeignKey(Contexts, blank=True, null=True, verbose_name='контекст', db_column='context')
    defaultip = CharField(max_length=25, blank=True, null=True, verbose_name='IP клиента', help_text='Если Вы знаете IP адрес телефона, Вы можете указать его здесь. Эти настройки будут использоваться при совершении вызовов на данный телефон, если он еще не зарегистрировался на сервере. После регистрации, телефон сам сообщит Asterisk под каким именем пользователя и IP адресом он доступен.')
    dtmfmode = CharField(max_length=8, default='info', editable=True, verbose_name='тип DTMF сигнализации', help_text='в режиме auto Asterisk будет использовать режим rfc2833 для передачи DTMF, по умолчанию, но будет переключаться в режим inband, для передачи DTMF сигналов, если удаленный клиент не укажет в SDP сообщении, что он поддерживает режим передачи DTMF - rfc2833', choices=DTMFS)
    fromuser = CharField(max_length=80, blank=True, null=True, editable=False, help_text='не используется, для совместимости')
    fromdomain = CharField(max_length=80, blank=True, null=True, editable=False, help_text='не используется, для совместимости')
    insecure = CharField(max_length=20, default='', blank=True, null=True, editable=True, verbose_name='игнорировать', choices=INVITE)
    language = CharField(max_length=2, editable=True, default='ru', verbose_name='язык')
    mailbox = CharField(max_length=15, blank=False, null=True, editable=False, help_text='Оставить пустым для автоподстановки')
    md5secret = CharField(max_length=80, blank=True, null=True, editable=False, verbose_name='MD5 пароль', help_text='не используется, для совместимости')
    deny = CharField(max_length=25, blank=True, null=True, editable=False, verbose_name='запрещенные подсети')
    permit = CharField(max_length=25, blank=True, null=True, editable=False, verbose_name='разрешенные подсети')
    mask = CharField(max_length=25, blank=True, null=True, editable=False, help_text='устарел')
    musiconhold = ForeignKey('asterfiles.SndFile', db_column='musiconhold', blank=True, null=True, editable=True, verbose_name='музыка ожидания', db_index=True, related_name='musiconhold')
    pickupgroup = CharField(max_length=80, blank=True, null=True, editable=False, help_text='не используется, для совместимости')
    qualify = CharField(max_length=5, default='no', blank=False, null=False, editable=True, verbose_name='SIP тест', help_text='если yes тогда Asterisk периодически (раз в 2 секунды) будет отправлять SIP сообщение типа OPTIONS, для проверки, что данное устройство работает и доступно для совершения вызовов. Если данное устройство, не ответит в течении заданного периода, тогда Asterisk рассматривает это устройство как выключенное и недоступное для совершения вызовов.', choices=YESNO)
    regexten = CharField(max_length=80, blank=True, null=True, editable=False, help_text='не используется, для совместимости')
    restrictcid = CharField(max_length=25, blank=True, null=True, editable=False, help_text='устарел')
    rtptimeout = CharField(max_length=3, blank=True, null=True, editable=False, help_text='не используется, для совместимости')
    rtpholdtimeout = CharField(max_length=3, blank=True, null=True, editable=False, help_text='не используется, для совместимости')
    secret = CharField(max_length=15, blank=True, null=False, editable=True, verbose_name='пароль', help_text='Для генерации оставьте пустым')
    setvar = CharField(max_length=25, blank=True, null=True, editable=False, help_text='устарел')
    disallow = CharField(max_length=100, editable=True, default='all', verbose_name='запрещенные кодеки')
    allow = CharField(max_length=100, editable=True, default='alaw', verbose_name='разрешенные кодеки')
    comment = TextField(blank=True, null=True, verbose_name='комментарий')
    trustrpid = CharField(max_length=3, blank=True, null=True, editable=True, default='no', verbose_name='Принимать RPID', choices=YESNO, help_text='Можно ли доверять полученному от SIP клиента Remote-Party-ID')
    sendrpid = CharField(max_length=3, blank=True, null=True, editable=True, default='yes', verbose_name='Передавать RPID', choices=YESNO, help_text='Необходимо передавать SIP клиенту Remote-Party-ID')
    videosupport = CharField(max_length=3, blank=True, null=True, editable=True, default='no', choices=YESNO, verbose_name='Поддержка видео')
    fullcontact = CharField(max_length=80, blank=True, null=True, editable=False, help_text='для совместимости')
    ipaddr = IPAddressField(blank=True, null=True, editable=True, verbose_name='последний IP', help_text='для совместимости')
    port = PositiveIntegerField(blank=True, null=True, editable=True, help_text='порт не dynamic клиентов')
    regseconds = BigIntegerField(blank=True, null=True, editable=True, help_text='для совместимости')
    username = CharField(max_length=100, blank=True, null=True, editable=True, help_text='для совместимости')
    regserver = CharField(max_length=100, blank=True, null=True, editable=True, help_text='для совместимости')
    useragent = CharField(max_length=100, blank=True, null=True, editable=True, help_text='для совместимости')
    defaultuser = CharField(max_length=100, blank=True, null=True, editable=True, help_text='для совместимости')
    useragent = CharField(max_length=100, blank=True, null=True, editable=False, help_text='для совместимости')
    lastms = CharField(max_length=100, blank=True, null=True, editable=False, help_text='для совместимости')
    defaultuser = CharField(max_length=15, blank=True, null=True, editable=False, help_text='сервер Asterisk будет посылать сообщения INVITE на username@defaultip')


    def gen_passwd(self):
        self.secret = ''.join(choice(string.letters.lower()+string.digits) for i in xrange(12))
        return self.save()

    def __unicode__(self):
        return u'%s (%s)' % (self.name, self.accountcode)

    def __init__(self,*args,**kwargs):
        super(Numbers,self).__init__(*args, **kwargs)
        if not self.secret.__len__():
            self.gen_passwd()

    class Meta:
        unique_together = (('name',),)
        ordering = ['name']
        verbose_name = 'номер'
        verbose_name_plural = 'номера'

class Voicemail(Model):
    YESNO=(
        ('yes','Да'),
        ('no', 'Нет'),
    )

    uniqueid = AutoField(primary_key=True,  blank=False, null=False, verbose_name='id', editable=False)
    payer = ForeignKey('address.Unit', blank=False, null=False, verbose_name='плательщик', db_index=True, db_column='customer_id', editable=False)
    context = CharField(max_length=10, blank=False, null=False, verbose_name='контекст', db_column='context', default=u'city', editable=False, db_index=True)
    mailbox = ForeignKey(Numbers, blank=False, null=False, verbose_name=u'Номер ящика', db_index=True, db_column='mailbox')
    password = PositiveSmallIntegerField(editable=False, blank=True, null=True, verbose_name=u'пароль', db_index=True)
    fullname = TextField(blank=True, null=True, verbose_name='полное имя')
    email = EmailField(blank=True, null=True, verbose_name='электронная почта', db_index=True)
    pager = EmailField(blank=True, null=True, verbose_name='E-mail для пейджера', db_index=True)
    tz = CharField(max_length=20, blank=False, null=False, verbose_name=u'часовой пояс', default=u'Europe/Moscow', choices=TIME_ZONES)
    attach = CharField(max_length=3, blank=False, null=False, verbose_name=u'прикреплять файлы', choices=YESNO, default='yes')
    saycid = CharField(max_length=3, blank=False, null=False, verbose_name=u'указывать ли номер', choices=YESNO, default='yes')
    review = CharField(max_length=3, blank=False, null=False, verbose_name=u'пересмотр', help_text='Если "Да", то дает возможность перезаписывать оставленное сообщение перед отправкой', choices=YESNO, default='no')
    operator = CharField(max_length=3, blank=False, editable=False, null=False, verbose_name=u'вызывать экстеншн 0', help_text='''Если "Да", то если вызывающий абонент нажмет 0 (ноль) в процессе проигрыша анонса, то выполнения плана набора продолжиться с екстеншена 'o' (сокр. от "Out"), в текущем контексте для голосовой почты. Эта функция может использоваться для перехода к вызову секретаря.''', choices=YESNO, default='no')
    envelope = CharField(max_length=3, blank=False, null=False, verbose_name=u'Региональные параметры', choices=YESNO, default='no', help_text='''Применять ли к сообщениям региональные параметры''')
    sayduration = CharField(max_length=3, blank=False, null=False, verbose_name=u'воспроизводить длительность', help_text='''Если "Да", то воспроизводит длительность сообщения''', choices=YESNO, default='no')
    saydurationm = PositiveSmallIntegerField(blank=True, null=False, verbose_name=u'начальная длительность воспроизведения', default=1, help_text='''Если "Воспроизводить длительность" "Да", то воспроизводит длительность сообщения если сообщение более %значение% минут''', db_index=True)
    sendvoicemail = CharField(max_length=3, blank=False, null=False, verbose_name=u'может пересылать сообщения', choices=YESNO, default='no')
    delete = CharField(max_length=3, blank=False, null=False, verbose_name=u'удалять сообщения после отправки', choices=YESNO, default='no', db_index=True)
    nextaftercmd = CharField(max_length=3, blank=False, null=False, verbose_name=u'проигрывать сдедующее после комманды', choices=YESNO, default='yes', db_index=True)
    forcename = CharField(max_length=3, blank=False, null=False, verbose_name=u'принудительно требовать ввод номера ящика', choices=YESNO, default='no')
    forcegreetings = CharField(max_length=3, blank=False, null=False, verbose_name=u'принудительно требовать запись приветствия', choices=YESNO, default='no')
    hidefromdir = CharField(max_length=3, blank=False, null=False, verbose_name=u'X3 hidefromdir', choices=YESNO, default='yes')
    stamp = DateTimeField(verbose_name=u'хз что это', blank=True, null=True, editable=False, db_index=True)
    attachfmt = CharField(max_length=80, default='wav49', blank=False, null=False, editable=False, verbose_name=u'Формат вложений')
    searchcontexts = CharField(max_length=3, blank=True, null=True, verbose_name=u'Пока не ясно но что-то там искать во всех контекстах', choices=YESNO, default='no', db_index=True)
    cidinternalcontexts = CharField(max_length=10, default='', blank=True, null=True, verbose_name="Пока не ясно cidinternalcontexts", db_index=True)
    exitcontext = CharField(max_length=10, default='', blank=True, null=True, verbose_name="Пока не ясно exitcontext", db_index=True)
    volgain = CharField(max_length=3, blank=False, null=False, verbose_name=u'сделать громче на (dB)', db_index=True, default='0.0')
    tempgreetwarn = CharField(max_length=3, blank=False, null=False, verbose_name=u'напоминать что установлено временное приветствие', choices=YESNO, default='yes', db_index=True)
    messagewrap = CharField(max_length=3, blank=False, null=False, verbose_name=u'воспроизводить более позние первыми', choices=YESNO, default='no', db_index=True)
    minpassword = PositiveSmallIntegerField(blank=False, null=False, verbose_name=u'минимальная длинна пароля', default=4, db_index=True)
    listen_control_forward_key = CharField(max_length=2, blank=False, null=False, verbose_name=u'клавиша перемотки вперед', default='6', db_column='listen-control-forward-key')
    listen_control_reverse_key = CharField(max_length=2, blank=False, null=False, verbose_name=u'клавиша перемотки назад', default='4', db_column='listen-control-reverse-key')
    listen_control_pause_key = CharField(max_length=2, blank=False, null=False, verbose_name=u'клавиша перемотки вперед', default='5', db_column='listen-control-pause-key')
    listen_control_restart_key = CharField(max_length=2, blank=False, null=False, verbose_name=u'клавиша повтора', default='2', db_column='listen-control-restart-key')
    listen_control_stop_key = CharField(max_length=2, blank=False, null=False, verbose_name=u'клавиша перемотки вперед', default='8', db_column='listen-control-stop-key')
    backupdeleted = CharField(max_length=2, default='25', blank=False, null=False, verbose_name=u'сообщений в корзине не более', db_index=True)

    class Meta:
         verbose_name = 'голосовая почта'
         verbose_name_plural = 'учетные записи голосовой почты'

    def __unicode__(self):
            return u'%s' % (self.mailbox)

    def gen_passwd(self):
        self.password = randint(1000,9999)

class Queue(Model):
    YESNO=(
        ('yes','Да'),
        ('no', 'Нет'),
    )
    YESNOONCE=(
        ('yes', u'Да'),
        ('no',  u'Нет'),
        ('once', u'Один раз')
    )
    TRUEFALSE=(
        (False,'Нет'),
        (True,'Да'),
    )
    STRATEGY=(
        ('ringall', u'Звонить во все доступные каналы пока не ответят'),
        ('leastrecent', u'Звонить в интерфейс который отвечал последним'),
        ('fewestcalls', u'Звонить тому кто принял меньше всего звонков в этой очереди'),
        ('random', u'Звонить совершенно случайно'),
        ('rrmemory', u'Round-Robin с памятью, Звонить по очереди помня кто последний отвечал'),
        ('wrandom', u'Звонить случайно но использовать веса'),
        ('linear', u'Звонить по порядку перечисленному в самой очереди'),
    )
    MONITOR_FORMAT=(
        ('gsm', u'GSM'),
        ('wav', u'WAV'),
        ('wav49', u'WAV, в котором записан GSM 6.10 кодек в MS формате'),
    )
    name = CharField(db_column='name', max_length=128, blank=False, null=False, verbose_name=u'имя', editable=True, db_index=True, primary_key=True)
    musiconhold = CharField(max_length=128, blank=True, null=True, editable=True, db_index=True)
    announce = CharField(max_length=128, blank=True, null=True, editable=True, db_index=True, verbose_name=u'Анонс', help_text=u'использовать анонс, проиграть этот файл анонса из файла',)
    context = ForeignKey("Contexts", blank=True, null=True, verbose_name='контекст', db_index=True, db_column='context', help_text=u'контекст в который будут перенаправлен ожидающий вызов набравший номер')
    timeout = PositiveIntegerField(blank=True, null=True, editable=True, db_index=True, help_text=u'столько секунд звонок без ответа на трубке прежде чем он перейдет на следующего агента')
    monitor_join = BooleanField(default=False, null=False, blank=False, verbose_name=u'Смешивать запись', choices=TRUEFALSE, db_index=True)
    monitor_format = CharField(max_length=128, blank=True, null=True, editable=True, db_index=True, choices=MONITOR_FORMAT)
    queue_youarenext = ForeignKey('asterfiles.SndFile', db_column='queue_youarenext', blank=True, null=True, editable=True, db_index=True, help_text=u'сообщение, которое будет сыграно: Теперь Вы первый на линии.', related_name='queue_youarenext')
    queue_thereare = ForeignKey('asterfiles.SndFile', db_column='queue_thereare', blank=True, null=True, editable=True, db_index=True, help_text=u'сообщение, которое будет сыграно: Ваша позиция в очереди', related_name='queue_thereare')
    queue_callswaiting = ForeignKey('asterfiles.SndFile', db_column='queue_callswaiting', blank=True, null=True, editable=True, db_index=True, help_text=u'сообщение, которое будет сыграно: ожидайте ответа', related_name='queue_callswaiting')
    queue_holdtime = ForeignKey('asterfiles.SndFile', db_column='queue_holdtime', blank=True, null=True, editable=True, db_index=True, help_text=u'сообщение, которое будет сыграно: приблизительное время ожидания', related_name='queue_holdtime')
    queue_minutes = ForeignKey('asterfiles.SndFile', db_column='queue_minutes', blank=True, null=True, editable=True, db_index=True, help_text=u'сообщение, которое будет сыграно: минут', related_name='queue_minutes')
    queue_seconds = ForeignKey('asterfiles.SndFile', db_column='queue_seconds', blank=True, null=True, editable=True, db_index=True, help_text=u'сообщение, которое будет сыграно: секунд', related_name='queue_seconds')
    queue_lessthan = ForeignKey('asterfiles.SndFile', db_column='queue_lessthan', blank=True, null=True, editable=True, db_index=True, help_text=u'сообщение, которое будет сыграно: менее', related_name='queue_lessthan')
    queue_thankyou =  ForeignKey('asterfiles.SndFile', db_column='queue_thankyou', blank=True, null=True, editable=True, db_index=True, help_text=u'сообщение, которое будет сыграно: спасибо за ожидание', related_name='queue_thankyou')
    queue_reporthold = ForeignKey('asterfiles.SndFile', db_column='queue_reporthold', blank=True, null=True, editable=True, db_index=True, help_text=u'сообщение, которое будет сыграно: время ожидания', related_name='queue_reporthold')
    announce_frequency = PositiveIntegerField(blank=True, null=True, editable=True, db_index=True, verbose_name=u'Частота анонса')
    announce_round_seconds = PositiveIntegerField(blank=True, null=True, editable=True, db_index=True, verbose_name=u'Округление', help_text=u'Округлять минуты/секунды до этого значения')
    announce_holdtime = CharField(max_length=5, blank=True, null=True, editable=True, db_index=True, choices=YESNOONCE, verbose_name=u'Анонс предпологаемого время ожидания')
    retry = PositiveIntegerField(blank=True, null=True, editable=True, db_index=True, verbose_name=u'Повтор', help_text=u'Сколько мы можем ждать прежде чем попробывать звонить участникам очереди снова')
    wrapuptime = PositiveIntegerField(blank=True, null=True, editable=True, db_index=True, verbose_name=u'время завершения', help_text='сделать паузу во столько секунд прежде чем снова передавать вызов этому участнику')
    maxlen = PositiveIntegerField(blank=True, null=True, editable=True, db_index=True, verbose_name=u'максимальный размер очереди')
    servicelevel = PositiveIntegerField(blank=True, null=True, editable=True, db_index=True, default=0, verbose_name=u'Уровень обслуживания', help_text=u'опция используется для статистики об уровне обслуживания. Вы устанавливаете период времени, в котором звонки должен быть дан ответ. По умолчанию он установлен в 0 (отключен).')
    strategy = CharField(max_length=128, blank=True, null=True, editable=True, db_index=True, default='ringall', choices=STRATEGY, verbose_name=u"стратегия")
    joinempty = CharField(max_length=128, blank=True, null=True, editable=True, db_index=True)
    leavewhenempty = CharField(max_length=128, blank=True, null=True, editable=True, db_index=True)
    eventmemberstatus = BooleanField(default=False, null=False, blank=False, verbose_name=u'генерировать события статуса', choices=TRUEFALSE, db_index=True)
    eventwhencalled = BooleanField(default=False, null=False, blank=False, verbose_name=u'генерировать события вызовов', choices=TRUEFALSE, db_index=True)
    reportholdtime = BooleanField(default=False, null=False, blank=False, verbose_name=u'сообщать сколько ждал абонент', help_text=u'Эта опция очень полезна. Когда установлено Да, член очереди, который отвечает, услышит, как долго абонент был в ожидании и слушал музыку ожидания.', choices=TRUEFALSE, db_index=True)
    memberdelay = PositiveIntegerField(blank=True, null=True, editable=True, db_index=True, help_text=u'Пауза в секундах, прежде чем агент будет соединен с абонентом из очереди', verbose_name=u'Пауза соединения', default=0)
    weight = PositiveIntegerField(default=1, blank=True, null=True, editable=True, db_index=True, verbose_name=u'вес очереди', help_text=u'Очереди с большим весом имеют больший приоритет в канале')
    timeoutrestart = BooleanField(null=False, blank=False, verbose_name='рестарт по таймауту', choices=TRUEFALSE, db_index=True, default=False, help_text=u'Если этот параметр имеет значение Да, и на входящей линии сигнал ЗАНЯТО или ПЕРЕГРУЗКА, агенты будут сброшенны по таймауту. Это может быть полезно с агентами, которые имеет разрешения для отмены вызова.')

    class Meta:
        unique_together = (('name', ),)
        verbose_name = u'Очередь'
        verbose_name_plural = u'Очереди'

    def __unicode__(self):
        return u'%s' % (self.name)

class QueueMember(Model):
    queue = ForeignKey("Queue", blank=False, null=False, verbose_name='очередь', db_index=True, db_column='queue_name')
    interface = CharField(max_length=128, blank=True, null=True, editable=True, db_index=True)
    penalty = PositiveIntegerField(blank=True, null=True, editable=True, db_index=True, verbose_name=u'пеннальти', help_text=u'Это какой-то приоритет. Идея в том, что система будет пытаться звонить первым агентам с более низким приоритетом, а агентов с высшим пеннальти будет пытаться вызвать после')

    class Meta:
        verbose_name = u'Участник очереди'
        verbose_name_plural = u'Участники очередей'

    def __unicode__(self):
        return u'%s' % (self.interface)

class QueueLog(Model):
    time = CharField(max_length=20, blank=False, null=True, editable=False, db_index=True)
    callid = CharField(max_length=32, blank=True, null=False, editable=False, db_index=True)
    queue = CharField(max_length=32, blank=True, null=False, editable=False, db_index=True, db_column='queuename')
    agent = CharField(max_length=32, blank=True, null=False, editable=False, db_index=True)
    event = CharField(max_length=32, blank=True, null=False, editable=False, db_index=True)
    data = TextField(blank=True, null=False, editable=False)

    class Meta:
        verbose_name = u'Статистика очередей'

    def __unicode__(self):
        time = datetime.fromtimestamp(float(self.time)).strftime('%Y-%m-%d %H:%M:%S')
        call = Cdr.objects.get(uniqueid=self.callid)
        return u'%s' % (call)


