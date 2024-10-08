LEXICON: dict[str, str] = {
    '/start': 'Привет! Я игровой бот!\n\nС моей помощью можно сыграть в квест '
              '<b>"Смертельный ремонт"</b>.\n\nЧтобы начать квест, '
              'отправьте команду /beginning\nЧтобы получить дополнительную '
              'информацию, отправьте команду /help',
    '/help': 'Сценарий квеста, в который можно сыграть с помощью данного бота,'
             ' написан с использованием большой языковой модели ChatGPT. Это '
             'небольшое космическое приключение, в котором вам предстоит '
             'починить двигатель космического корабля, чтобы изменить его '
             'курс и избежать столкновения с планетой\n\nСписок доступных '
             'команд:\n\n/beginning - начать квест сначала\n'
             '/continue - продолжить квест\n'
             '/cancel - выйти из квеста\n\n'
             '<b>Давайте играть!</b>',
    '/cancel': 'Вы вышли из квеста/\n\nЧтобы начать сначала, отправьте '
               'команду /beginning',
    '/beginning': 'Квест <b>"Смертельный ремонт"</b> начинается! Успехов вам!',
    'beginning_1': 'Вы единственный член экипажа, оставшийся на космическом '
                   'корабле "Атлантис".',
    'beginning_2': 'На корабле произошла авария и все члены команды были '
                   'эвакуированы на спасательные шаттлы, потому что '
                   'получили ранения разной степени тяжести.',
    'beginning_3': 'Вам повезло больше других - почти ни царапины, поэтому вы '
                   'решили остаться, чтобы попробовать починить двигатель, '
                   'и изменить курс корабля.',
    'beginning_4': 'А иначе он упадет на планету, с которой происходит '
                   'стремительное сближение...',
    'beginning_5': 'Предварительный анализ планеты дает 87%-ную уверенность '
                   'в том, что планета обитаема, поэтому катастрофы нужно '
                   'избежать чего бы вам это ни стоило...',
    'beginning_6': 'Вы готовы принять вызов и спасти планету?',
    'yes_ready': 'Конечно, готов!',
    'maybe_ready': 'Ну, а что мне остается...',
    'no_ready': 'Нет, я не смогу...',
    'yes_ready_answer': 'Молодец, солдат! Так держать!\nДавайте спасем планету!',
    'maybe_ready_answer': 'Правильное решение, боец!\n\nНе отчаивайтесь. '
                          'Только на вас вся надежда',
    'no_ready_answer': 'Ничтожество! Ты не заслуживаешь никакого уважения!\n'
                       'И за что тебя только выбрали в команду?',
    'no_ready_answer_1': 'Планетарная трагедия на твоей совести, да и тебе '
                         'самому недолго осталось...',
    'quest_failed': 'МИССИЯ ПРОВАЛЕНА',
    'quest_started_1': 'Вы находитесь в двигательном отсеке космического '
                       'корабля "Атлантис". Перед вами огромный двигатель, '
                       'который должен был давать кораблю скорость и '
                       'маневренность.',
    'quest_started_2': 'Но сейчас двигатель выглядит как груда металлолома. '
                       'Он поврежден в нескольких местах, из него торчат '
                       'провода и трубы, из него идет дым и искры...',
    'quest_started_3': 'Вы слышите треск и свист, который свидетельствует '
                       'о том, что двигатель на грани полной поломки...',
    'quest_started_4': 'Вы понимаете, что нужно поскорее запустить двигатель, '
                       'иначе катастрофы не миновать.',
    'start_state_available_actions': 'Будьте осторожны в своих действиях, '
                                     'но не теряйте время! Ставки очень '
                                     'высоки!\n\nЧто вы собираетесь делать?',
    'look_around': 'Осмотреться',
    'see_backpack': 'Заглянуть в рюкзак',
    'get_out_engine_compartment': 'Покинуть двигательный отсек',
    'look_around_eng_answ_1': 'Кроме поломанного двигателя вы видите дверь, '
                              'которая ведет в другую часть космического '
                              'корабля.',
    'look_around_eng_answ_2': 'C противоположной от двери стороны распложен '
                              'илиндрический служебный отсек с некоторыми '
                              'системами жизнеобеспечения корабля.',
    'look_around_eng_answ_3': 'По всем отсеку идут различные трубки, провода, '
                              'датчики и панели управления, которые соединяют '
                              'и контролируют все компоненты двигательного '
                              'отсека.',
    'look_around_eng_answ_4': 'В целом, ничего интересного',
    'look_around_eng_answ_5': 'Двигатель починить вы не можете, потому что у '
                              'вас нет инструкции, необходимых инструментов и '
                              'запасных деталей. Что дальше?',
    'backpack_items': 'Вы можете воспользоваться следующими вещами из '
                      'вашего рюкзака:',
    'backpack_empty': 'Ваш рюкзак пуст',
    'instruction': 'Инструкция',
    'first_aid_kit': 'Аптечка',
    'engineering_compartment_1': 'Вы попали в инженерное отделение корабля. '
                                 'Перед вами огромный отсек, заполненный '
                                 'разнообразными механизмами, трубами, '
                                 'проводами и панелями.',
    'engineering_compartment_2': 'Вы слышите гул, шипение радиосвязи, щелчки '
                                 'реле и писк приборных панелей, сообщающих, '
                                 'что что-то не в порядке. Но вы итак в '
                                 'курсе.',
    'engineering_compartment_3': 'Возможно, здесь можно найти что-нибудь '
                                 'полезное для вашей миссии.\n\nЧто вы '
                                 'собираетесь предпринять?',
    'return_to_engine_compartment': 'Вернуться в двигательный отсек',
    'look_around_engineering_answ_1': 'Сзади вас находится вход в '
                                      'двигательный отсек, из которого вы '
                                      'только что пришли.',
    'look_around_engineering_answ_2': 'Слева от вас вход в медицинский блок, '
                                      'а прямо - выход на мостик.',
    'look_around_engineering_answ_3': 'У дальней правой стены отделения, в '
                                      'котором вы сейчас находитесь, стоит '
                                      'стеллаж с ящиками и инструментами в '
                                      'этих ящиках.',
    'look_around_engineering_answ_4': 'В одном из углов отсека находится '
                                      'большой железный шкаф с надписью '
                                      '"Spare parts".',
    'look_around_engineering_answ_5': 'Как планируете поступить дальше?',
    'go_to_med_compartment': 'Идти в медицинский блок',
    'go_to_bridge': 'Идти на мостик',
    'take_spare_parts': 'Взять запчасти',
    'take_tools': 'Взять инструменты'



}

LEXICON_COMMANDS: dict[str, str] = {
    '/beginning': 'Начать квест сначала',
    '/continue': 'Продолжить квест',
    '/help': 'Справка по работе бота'
}
