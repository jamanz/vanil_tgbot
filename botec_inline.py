import logging

from dotenv import load_dotenv
from telegram import __version__ as TG_VER
import os

try:

    from telegram import __version_info__

except ImportError:

    __version_info__ = (0, 0, 0, 0, 0)  # type: ignore[assignment]


if __version_info__ < (20, 0, 0, "alpha", 1):

    raise RuntimeError(

        f"This example is not compatible with your current PTB version {TG_VER}. To view the "

        f"{TG_VER} version of this example, "

        f"visit https://docs.python-telegram-bot.org/en/v{TG_VER}/examples.html"

    )

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, Update

from telegram.ext import (

    Application,

    CallbackQueryHandler,

    CommandHandler,


    ContextTypes,

    ConversationHandler,

    MessageHandler,

    filters

)


def pprint_tree_data(usr_dict):
    text = 'Number: ' + str(usr_dict.get('Number', '  ')) + '\n'
    text += 'Height: ' + str(usr_dict.get('Height', '  ')) + '\n'
    text += 'Stem Diameter: ' + str(usr_dict.get('Stem Diameter', '  ')) + '\n'
    text += 'Type: ' + str(usr_dict.get('Type', '  ')) + '\n'
    text += 'Altitude: ' + str(usr_dict.get('Altitude', '  ')) + '\n'
    text += 'Location: ' + str(usr_dict.get('Location', '  ')) + '\n'


    return text


# Enable logging

logging.basicConfig(

    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO

)

logger = logging.getLogger(__name__)


# Stages

ADD_DATA = 1
SHOW_REC = 2


HEIGHT, STEM_D, T_TYPE, ALTITUDE, LOCATION = range(5, 10)
NUMBER = 18

FEATURE_MAP = {
    HEIGHT: "Height",
    STEM_D: "Stem Diameter",
    T_TYPE: "Type",
    ALTITUDE: "Altitude",
    LOCATION: "Location",
    NUMBER: "Number",
}



CURRENT_FEATURE = 10
TYPING = 11
SELECTION_ACTION = 12
SELECTION_FEATURES = 13
DONE = 17
SHOWING = 19

START_OVER = 14
TYPE_TYPING = 15
LOCATION_TYPING = 16


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:

    """Send message on `/start`."""

    # Get user that sent /start and log his name

    # user = update.message.from_user
    # logger.info("User %s started the conversation.", user.first_name)

    if not context.user_data.get('TREES'):
        context.user_data['TREES'] = []

    keyboard = [
        [InlineKeyboardButton("Start Data Acquisition Session", callback_data=str(ADD_DATA))],
        [InlineKeyboardButton("Show Recorded", callback_data=str(SHOW_REC))],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)


    if context.user_data.get(START_OVER):
        # await update.callback_query.answer()
        await update.callback_query.edit_message_text(
            text="Hi, I'm bot to facilitate our tree data recordings.", reply_markup=reply_markup
        )
    else:
    # Send message with text and appended InlineKeyboard
        await update.message.reply_text("Hi, I'm bot to facilitate our tree data recordings", reply_markup=reply_markup)

    context.user_data[START_OVER] = False

    # Tell ConversationHandler that we're in state `SELECTION_ACTION` now

    return SELECTION_ACTION



async def add_data(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:

    """Show new choice of buttons"""

    # await query.answer()


    keyboard = [

        [
            InlineKeyboardButton("Number", callback_data=str(NUMBER)),
            InlineKeyboardButton("Height", callback_data=str(HEIGHT)),
            InlineKeyboardButton("Stem Diameter", callback_data=str(STEM_D)),

        ],
        [
            InlineKeyboardButton("Type", callback_data=str(T_TYPE)),
            InlineKeyboardButton("Altitude", callback_data=str(ALTITUDE)),
            InlineKeyboardButton("Location", callback_data=str(LOCATION))
        ],
        [
            InlineKeyboardButton("Done", callback_data="DONE"),
        ]

    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    current_tree_data = context.user_data

    if not context.user_data.get(START_OVER):

        await update.callback_query.answer()
        await update.callback_query.edit_message_text(
            text=f"Current tree data:\n🌴 🌴 🌴\n{pprint_tree_data(current_tree_data)}", reply_markup=reply_markup
        )
    else:
        await update.message.reply_text(text=f"Current tree data:\n🌴 🌴 🌴\n{pprint_tree_data(current_tree_data)}",
                                        reply_markup=reply_markup)

    context.user_data[START_OVER] = False

    return SELECTION_FEATURES


async def ask_for_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info(f"callback query is {update.callback_query.data}")
    context.user_data[CURRENT_FEATURE] = update.callback_query.data
    str_feature = FEATURE_MAP[int(update.callback_query.data)]
    logger.info("User choise to update %s", str_feature)
    text = f'Okey, tell me {str_feature}.'

    await update.callback_query.answer()
    if str_feature == 'Type':
        keyboard = [
            [InlineKeyboardButton('Olive', callback_data='Olive')],
            [InlineKeyboardButton('Ficus', callback_data='Ficus')],
            [InlineKeyboardButton('Other', callback_data='Other')]
        ]
        context.user_data[TYPE_TYPING] = True
        await update.callback_query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
        return TYPE_TYPING
    elif str_feature == 'Location':
        text = f"Ok. Send me location via Telegram"
        await update.callback_query.edit_message_text(text)
        return LOCATION_TYPING

    else:
        await update.callback_query.edit_message_text(text)

        return TYPING


async def save_input(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_data = context.user_data

    str_feature = FEATURE_MAP[int(user_data[CURRENT_FEATURE])]
    context.user_data[str_feature] = update.message.text

    user_data[START_OVER] = True
    return await add_data(update, context)


async def save_type_input(update, context):
    user_data = context.user_data

    str_feature = FEATURE_MAP[int(user_data[CURRENT_FEATURE])]
    logger.info(f"TREE TYPE RECIEVED: {update.callback_query.data}")
    context.user_data[str_feature] = update.callback_query.data
    # user_data[START_OVER] = True
    return await add_data(update, context)


async def save_location_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_data = context.user_data
    str_feature = FEATURE_MAP[int(user_data[CURRENT_FEATURE])]
    logger.info(f"LOCATION RECIEVED: {update.message.location}")
    context.user_data[str_feature] = f"{update.message.location.longitude}, {update.message.location.latitude}"
    user_data[START_OVER] = True
    return await add_data(update, context)


async def end_recording(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:

    """Returns `ConversationHandler.END`, which tells the

    ConversationHandler that the conversation is over.

    """
    logger.info("WE INSIDE END")
    # query = update.callback_query
    # await update.callback_query.answer()
    context.user_data[START_OVER] = True
    features = ('Number', 'Height', 'Stem Diameter', 'Type', 'Altitude', 'Location')

    current_tree = {feature[0]: feature[1] for feature in context.user_data.items() if feature[0] in features}
    logger.info(f'TREE FEATURES AFTER FILTER: {current_tree}')

    for k in context.user_data:
        if k in features:
            context.user_data[k] = ''
    context.user_data['TREES'].append(current_tree)

    await update.callback_query.answer()
    await start(update, context)
    return SELECTION_ACTION


async def show_all(update, context):
    logger.info("We inside SHOWING")
    buttons = [[InlineKeyboardButton(text="Back", callback_data="DONE")]]

    keyboard = InlineKeyboardMarkup(buttons)

    text = ''
    for tree in context.user_data['TREES']:
        text += pprint_tree_data(tree) + '\n'

    await update.callback_query.answer()
    await update.callback_query.edit_message_text(text=f"{text}", reply_markup=keyboard)

    context.user_data[START_OVER] = True

    return SHOWING

def main() -> None:

    """Run the bot."""

    # Create the Application and pass it your bot's token.
    Token = os.getenv('TGBOT_API_KEY')
    application = Application.builder().token(Token ).build()


    # Setup conversation handler with the states FIRST and SECOND

    # Use the pattern parameter to pass CallbackQueries with specific

    # data pattern to the corresponding handlers.

    # ^ means "start of line/string"

    # $ means "end of line/string"

    # So ^ABC$ will only allow 'ABC'



    conv_handler = ConversationHandler(

        entry_points=[CommandHandler("start", start)],

        states={
            SELECTION_ACTION: [
                CallbackQueryHandler(add_data, pattern=f"^{ADD_DATA}$"),
                CallbackQueryHandler(show_all, pattern=f"^{SHOW_REC}$")
            ],

            SHOWING: [
                CallbackQueryHandler(start, pattern=f"^DONE$")
            ],

            SELECTION_FEATURES: [
                CallbackQueryHandler(ask_for_input,
                                     pattern=f"^{NUMBER}$|^{HEIGHT}$|^{STEM_D}$|^{T_TYPE}$|^{ALTITUDE}$|^{LOCATION}$")
            ],
            TYPING: [
              MessageHandler(filters.TEXT, save_input),
            ],

            TYPE_TYPING: [
                CallbackQueryHandler(save_type_input, pattern=f"^Olive$|^Ficus$|^Other$")
            ],

            LOCATION_TYPING: [
                MessageHandler(filters.LOCATION, save_location_input)
            ],

        },

        fallbacks=[
            CommandHandler("start", start),
            CallbackQueryHandler(end_recording, pattern=f"^DONE$")
        ],

    )


    # Add ConversationHandler to application that will be used for handling updates

    application.add_handler(conv_handler)


    # Run the bot until the user presses Ctrl-C

    application.run_polling()



if __name__ == "__main__":
    load_dotenv()

    main()