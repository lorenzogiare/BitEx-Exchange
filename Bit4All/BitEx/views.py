from PyQt5.QtWidgets import (QWidget, QMainWindow, 
    QSlider, QDoubleSpinBox, QLabel,QLineEdit, QDialogButtonBox, QPushButton, QTableWidget, QLCDNumber, QTableWidgetItem, QGraphicsView, QGraphicsScene )
from PyQt5 import uic
from PyQt5.QtCore import QRect
from pyqtgraph import PlotWidget, mkPen
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
import os
from .models import Profile, Wallet, Order
from random import randrange
from django.utils import timezone
import tkinter as tk
from tkinter import ttk



class loginWindow(QWidget):

    """ defines the login window and the useful widgets """
    def __init__(self):

        # makes available all methods of parent class 
        super(loginWindow, self).__init__()

        # Load Ui login file (for now, when the ui file is complete i will convert to fixed python file)
        uic.loadUi(os.path.join(os.path.dirname(__file__), "gui_designs/login.ui"), self)

        self.setFixedSize(700,750)

        # username and password
        self.username = self.findChild(QLineEdit, 'username_login')
        self.password = self.findChild(QLineEdit, 'password_login')
        self.password.setEchoMode(QLineEdit.Password) # censors password 

        # login dialog buttons
        self.login_dialog = self.findChild(QDialogButtonBox, 'confirm_login')
        self.login_dialog.accepted.connect(self.check_login_validity)
        self.login_dialog.rejected.connect(self.clear_fields)

        # registration button
        self.register_button = self.findChild(QPushButton, 'go_to_registration_button')
        self.register_button.clicked.connect(self.go_to_registration)

        # incorrect login error message
        self.message = self.findChild(QLabel, 'login_error_message')
    
    """ when cancel is pressed, clears username, password and error message fields """
    def clear_fields(self):
        self.username.setText(None)
        self.password.setText(None)
        self.message.setText(None)

    """ 
    checks if input username and password are correct, if so, loggs ther user
    and starts the main window 
    """
    def check_login_validity(self):
        username, password = self.username.text(), self.password.text()
        self.user = authenticate(username=username, password=password)

        if self.user is not None:
            self.go_to_main()
        else: 
            # print error message 
            try:
                User.objects.get(username=username)
                self.message.setText('input password is wrong, try again')
            except User.DoesNotExist:
                self.message.setText('incorrect Login, check your username')

    """ 
    closes current login window and opens the main interface 
    (after successfull login) 
    """
    def go_to_main(self):

        #closes login window
        self.close()

        #Inizializing the main interface
        self.main_window = mainWindow(profile=Profile.objects.get(user=self.user))
        self.main_window.show() 

    """ closes current login window and opens the registration interface """
    def go_to_registration(self):

        #closes login window
        self.close()

        #Inizializing the registration interface
        self.registration_window = registrationWindow()
        self.registration_window.show()


class registrationWindow(QWidget):

    """ defines the registration window and the useful widgets """
    def __init__(self):

        # makes available all methods of parent class 
        super(registrationWindow, self).__init__()

        # Load Ui login file (for now, when the ui file is complete i will convert to fixed python file)
        uic.loadUi(os.path.join(os.path.dirname(__file__), "gui_designs/registration.ui"), self)

        self.setFixedSize(900,750)

        # declare user info
        self.first_name = self.findChild(QLineEdit, 'first_name_register')
        self.last_name = self.findChild(QLineEdit, 'last_name_register')
        self.username = self.findChild(QLineEdit, 'username_register')

        # declare password fields
        self.password = self.findChild(QLineEdit, 'password_register')
        self.password.setEchoMode(QLineEdit.Password) # censors password
        self.repeat_password = self.findChild(QLineEdit, 'password_register_2')
        self.repeat_password.setEchoMode(QLineEdit.Password) # censors password

        # declare error field
        self.error_message = self.findChild(QLabel, 'message')
        
        # declare and connect dialog buttons
        self.confirm_registration_dialog = self.findChild(QDialogButtonBox, 'confirm_registration')
        self.confirm_registration_dialog.accepted.connect(self.check_registration_validity)
        self.confirm_registration_dialog.rejected.connect(self.clear_fields)

        # declare <go to login> button
        self.go_to_login_button = self.findChild(QPushButton, 'go_to_login_button')
        self.go_to_login_button.clicked.connect(self.go_to_login)
    
    """ checks if form is correcly filled, if so, registers the user and opens the main interface """
    def check_registration_validity(self):
        
        # are all fields filled?
        if not self.all_fields_filled():
            self.error_message.setText('all fields must be filled!')
            return False
        
        # is username available?
        if not self.is_username_available():
            self.error_message.setText('this username is already taken, try another one...')
            return False

        # was the password repeated correctly?
        if not self.password.text() == self.repeat_password.text():
            self.error_message.setText('the two passwords do not match!')
            return False
    
        #  registers the user and displays the popup message
        btc=self.register_user()
        self.popupmsg(btc=btc)

        # open main interface
        self.go_to_main(profile=self.profile)
        
    """ clears all fields when CANCEL is pressed """
    def clear_fields(self):

        [field.setText(None) for field in 
            [self.username, self.first_name, self.last_name, self.password, self.repeat_password, self.error_message]
        ]

    """ checks if all fields are filled """
    def all_fields_filled(self):

        for field in [self.username, self.first_name, self.last_name, self.password, self.repeat_password]:
            if field.text().strip() == '': return False
        return True

    """ checks if username is already taken """
    def is_username_available(self):
        if User.objects.filter(username=self.username.text()).exists():
            return False
        return True

    """ creates User and Profile models and assigns the random bitcoin balance """
    def register_user(self):
        
        user = User(
                first_name=self.first_name.text(),
                last_name=self.last_name.text(),
                username=self.username.text(),
            )
        
        user.set_password(self.password.text())
        user.save()

        starting_btc_balance = randrange(1,10,1)

        self.profile = Profile(
            user = user,
            wallet={
                'btc_balance': starting_btc_balance,
                'starting_btc_balance': starting_btc_balance,
                'usd_balance':  0,
            }
        )

        self.profile.save()

        print(f"successfull registration!, welcome {user.username}")

        return starting_btc_balance

    """ go to login window (when button is clicked) """
    def go_to_login(self):

        #closes registration window
        self.close()

        #Inizializing the login interface
        self.login_window = loginWindow()
        self.login_window.show()

    """ closes current registration interface and opens main UI (when registration is successful) """
    def go_to_main(self, profile):

        #closes registration window
        self.close()

        #Inizializing the login interface
        self.main_window = mainWindow(profile=profile)
        self.main_window.show()

    """ displays a popup message showing how many bitcoins the new user received """
    def popupmsg(self, btc):
        popup = tk.Tk()
        popup.wm_title(" CONGRATULATIONS! ")
        label = ttk.Label(popup, text=f"you have been awarded {btc} BITCOINS",  font=("century", 20))
        label.pack(side="top", fill="x", pady=10, padx=20)
        B1 = ttk.Button(popup, text="OK", command = popup.destroy)
        B1.pack(pady=20, padx=20)
        popup.mainloop()


class mainWindow(QMainWindow):

    ''' exchange window '''
    def __init__(self, profile):
        super(mainWindow, self).__init__()

        #Load main Ui file
        uic.loadUi(os.path.join(os.path.dirname(__file__), "gui_designs/BitEx_GUI.ui"), self)

        self.setFixedSize(1600,1250)

        # currently logged account
        self.profile = profile
        
        # ------- MAKE ORDER -------------------------------------------------------

        # BUY
        self.amount_trade_buy = self.findChild(QDoubleSpinBox, 'amount_buy_order')
        self.price_trade_buy = self.findChild(QDoubleSpinBox, 'price_buy_order')

        self.amount_trade_buy.setRange(0.0001, 1000000)
        self.price_trade_buy.setRange(0.1, 10000000)

        self.send_buy_order = self.findChild(QPushButton, 'send_buy_order')
        self.cancel_buy_order = self.findChild(QDialogButtonBox, 'cancel_buy_order')
        
        # SELL
        self.amount_trade_sell = self.findChild(QDoubleSpinBox, 'amount_sell_order')
        self.price_trade_sell = self.findChild(QDoubleSpinBox, 'price_sell_order')

        self.amount_trade_sell.setRange(0.001, self.profile.wallet['btc_balance'])
        self.price_trade_sell.setRange(0.1, 10000000)

        self.send_sell_order = self.findChild(QPushButton, 'send_sell_order')
        self.cancel_sell_order = self.findChild(QDialogButtonBox, 'cancel_sell_order')

        # BUTTONS & MESSAGES
        self.order_error_message = self.findChild(QLabel, 'order_error_message')

        self.send_buy_order = self.findChild(QPushButton, 'send_buy_order')
        self.send_sell_order = self.findChild(QPushButton, 'send_sell_order')

        self.send_buy_order.clicked.connect(self.send_order_buy)
        self.send_sell_order.clicked.connect(self.send_order_sell)

        # ------- ORDER BOOK --------------------------------------------------------

        self.buy_orders_table = self.findChild(QTableWidget, 'buy_orders_table')
        self.sell_orders_table = self.findChild(QTableWidget, 'sell_orders_table')

        self.load_tables_data_buy(), self.load_tables_data_sell()

        # ------- USER PANEL --------------------------------------------------------

        # user profile
        self.first_name = self.findChild(QLabel, 'first_name')
        self.first_name.setText(profile.user.first_name)
        self.last_name = self.findChild(QLabel, 'last_name')
        self.last_name.setText(profile.user.last_name) 
        self.username = self.findChild(QLabel, 'username')
        self.username.setText(profile.user.username)
        
        # user balance
        self.user_btc_balance = self.findChild(QLCDNumber, 'user_btc_balance')
        self.user_usd_balance = self.findChild(QLCDNumber, 'user_usd_balance')

        # -------- MY OPEN ORDERS ---------------------------------------------------

        self.my_open_orders_table = self.findChild(QTableWidget, 'my_open_orders_table')

        self.load_my_open_orders_table()

        # -------- MY ORDER HISTORY -------------------------------------------------

        self.my_order_history_table = self.findChild(QTableWidget, 'my_order_history_table')

        self.load_personal_history_table()

        # -------- GRAPH ------------------------------------------------------------

        self.graph = self.findChild(QGraphicsView, 'graphicsView')
        self.graphicsview = PlotWidget(self.graph)
        self.graphicsview.setGeometry(QRect(0, 0, 700, 650))
        self.graphicsview.setBackground('w')
        self.graphicsview.showGrid(x=True, y=True)
        self.plot()
        
        # -------- NET PROFIT OR LOSS -----------------------------------------------
        self.net_btc_profit = self.findChild(QLCDNumber, 'btc_profit')
        self.net_usd_profit = self.findChild(QLCDNumber, 'usd_profit')

        # --------- UPDATE INTERFACE BUTTON -----------------------------------------
        self.update_interface_btn = self.findChild(QPushButton, 'update_interface_button')

        self.update_interface_btn.clicked.connect(self.update_interface)

        # -------- LOAD DATA INSIDE INTERFACE ---------------------------------------
        self.update_interface()
    

    ''' plots the prices of the filled trades over time'''
    def plot(self):
        data = Order.objects.filter(filled=True).order_by('date_filled')
        prices = [order.price for order in data]
        
        self.graphicsview.plot(prices, pen=mkPen(color=(0, 0, 0)), width = 15)

    ''' 
    refers to send_order method 
    (could not pass argument 'buy' to method directly in the connection of the "send order" button)
    '''
    def send_order_buy(self):
        self.send_order(type='buy')

    ''' 
    refers to send_order method 
    (could not pass argument 'sell' to method directly in the connection of the "send order" button)
    '''
    def send_order_sell(self):
        self.send_order(type='sell')

    ''' creates order, adds it to the order book and to personal open orders '''
    def send_order(self, type):

        # create order document
        order = self.create_order(type=type)

        if order:

            # update user balance (subtracts quantity bound to the order)
            self.update_user_balance(order=order)
            
            # fill the order (and its counterparts) if possible (also updates wallets)
            self.fill_match(order)
        
    ''' create the order object if valid '''
    def create_order(self, type):
        
        if not self.order_is_valid(type=type):
            return(False)

        order = Order(
            user = self.profile.user.username,
            type = type,
            amount = self.get_amount_order(type=type),
            price = self.get_price_order(type=type),
            date_created = timezone.now(),
        )

        order.save()

        return order
    
    ''' does the user have enough funds to send this order? the order can't have price or amount set to 0 '''
    def order_is_valid(self, type):

        usd_balance = self.profile.wallet['usd_balance']
        btc_balance = self.profile.wallet['btc_balance']

         
        if type=='buy':

            order_value = self.price_trade_buy.value() * self.amount_trade_buy.value()

            if usd_balance < order_value or self.price_trade_buy.value() == 0 or self.amount_trade_buy.value() == 0 : 
                self.order_error_message.setText("your USD balance is insufficient!")
                return False

        if type=='sell':
            
            print(f'selling amount: {self.amount_trade_sell}')

            if btc_balance < self.amount_trade_sell.value() or self.price_trade_sell.value()== 0 or self.amount_trade_sell.value() == 0:
                self.order_error_message.setText("your Bitcoin balance is insufficient!")
                return False
        


        return True
    
    ''' get the amount of the order (buy or sell)'''
    def get_amount_order(self, type):

        if type == 'buy':
            return self.amount_trade_buy.value()

        if type == 'sell':
            return self.amount_trade_sell.value()

    ''' get price of the order (buy or sell)'''
    def get_price_order(self, type):

        if type == 'buy':
                return self.price_trade_buy.value()

        if type == 'sell':
            return self.price_trade_sell.value()
    
    ''' update balance after order is sent '''
    def update_user_balance(self, order):

        if order.type == 'buy':
            self.profile.wallet['usd_balance'] -= self.amount_trade_buy.value() * self.price_trade_buy.value()

        if order.type == 'sell':
            self.profile.wallet['btc_balance'] -= self.amount_trade_sell.value()
        
        self.profile.save()
 
    ''' 
        this function iterates over the matching counterparts (orders, if there are any) and fills both according to their specifics,
        this happens until our order is either filled completely or there are no more matching counterparts. 
        [ At the end of every counterpart's evaluation both wallets are also updated ]
    '''
    def fill_match(self, order):

        matches = self.get_matches(order)

        # if there are no matches, leave order pending
        if not matches:
            print('there are no matches...')
            return False
        
        print(f'your matches:{matches}')
        
        # begin iteration over the matches until my order is either filled or there are no more matches available
        while matches and order.filled is False:

            counterpart = matches[0]  # the first in the queryset ( greatest difference between ask and offer price )
            print(f'\n the current counterpart is: {counterpart}')

            counterpart_real_amount = counterpart.amount
            order_real_amount = order.amount

            # the real amount is the part of our and the counterpart's order not already filled
            if counterpart.quote_filled != 0 : counterpart_real_amount = counterpart.amount * (1 - counterpart.quote_filled)
            order_real_amount = order.amount * (1 - order.quote_filled) # (our order won't be fully filled because of the iteration's condition)

            print(f"the counterpart's real amount is: {counterpart_real_amount}")
            print(f"our order's real amount is: {order_real_amount}")

            #  the counterpart order has a real amount superior or equal to our order (order filled, iteration stops)
            if counterpart_real_amount > order_real_amount:
                print("the counterpart's real amount is greater, our order is going to be fully filled")
                
                # delta quote of orders newly filled
                delta_filled_order = 1 - order.quote_filled
                delta_filled_counterpart = 1 - ((counterpart_real_amount - order_real_amount) / counterpart.amount) - counterpart.quote_filled

                order.filled = True
                order.quote_filled = 1
                order.date_filled = timezone.now()

                #counterpart's order updates filled percentage 
                counterpart.quote_filled = 1 - ((counterpart_real_amount - order_real_amount) / counterpart.amount)

            
            # the counterpart order has a real amount inferior to our order (must continue iteration)
            elif counterpart_real_amount < order_real_amount:

                print("our order's real amount is greater, the counterpart is gonna be filled fully")

                # quote of order newly filled
                delta_filled_order = 1 - ((order_real_amount - counterpart_real_amount) / order.amount) - order.quote_filled
                delta_filled_counterpart = 1 - counterpart.quote_filled

                counterpart.filled = True 
                counterpart.quote_filled = 1
                counterpart.date_filled = timezone.now()

                # our order's fulfillment's percentage is updated
                order.quote_filled = 1 - ((order_real_amount - counterpart_real_amount) / order.amount)

            else:

                print('the real amounts coincide, both are completely filled')

                # quote of order newly filled
                delta_filled_order = 1 - order.quote_filled
                delta_filled_counterpart = 1- counterpart.quote_filled

                counterpart.filled, order.filled = True, True
                counterpart.quote_filled, order.quote_filled = 1, 1
                counterpart.date_filled, order.date_filled = timezone.now(), timezone.now()
            

            order.save()
            counterpart.save()

            print(f"the counterpart's order is now filled to {counterpart.quote_filled}")
            print(f"our order is now filled to {order.quote_filled}")

            # UPDATE portfolios of user and counterpart 
            self.update_portfolios(
                order = order,
                delta_filled_order=delta_filled_order,
                counterpart = counterpart,
                delta_filled_counterpart=delta_filled_counterpart
                )

            #remove counterpart from matches
            matches = matches.exclude(_id=counterpart._id)
            print(f"your remaining matches are:{matches}")

    ''' gets all the orders in the order book that satisy our order, either fully or partially'''
    def get_matches(self, order):

        if order.type == 'buy':
            valid_matches = Order.objects.filter(type='sell', price__lte=order.price).exclude(user=self.profile.user.username).exclude(filled=True)

        if order.type == 'sell':
            valid_matches = Order.objects.filter(type='buy', price__gte=order.price).exclude(user=self.profile.user.username).exclude(filled=True).order_by('price').reverse()

        if valid_matches :
            return valid_matches
        else: return False

    ''' 
        updates our wallet and the one of the user that sent the counterpart order 
        ( also gives back the difference to the buyer if bid/ask prices don't match)
    '''    
    def update_portfolios(self, delta_filled_order, order, delta_filled_counterpart, counterpart):
    
        # get the profile of the counterpart
        user_counterpart = User.objects.get(username=counterpart.user)
        profile_counterpart = Profile.objects.get(user=user_counterpart)

        if order.type == 'buy':

            # give me what i bought
            self.profile.wallet['btc_balance'] += delta_filled_order * order.amount
            print(f" my bitcoin balance increases of {delta_filled_order * order.amount} BTC")
            # give me back the rest of the unspent order money ( if the selling price is lower than my offer )
            self.profile.wallet['usd_balance'] += delta_filled_order * order.amount * (order.price - counterpart.price)
            print(f" i get back the unspent money : {delta_filled_order * order.amount * (order.price - counterpart.price)} USD ")
            # give the counterpart the amount he sold for
            profile_counterpart.wallet['usd_balance'] += delta_filled_counterpart * counterpart.amount * counterpart.price
            print(f" the counterpart gets {delta_filled_counterpart * counterpart.amount * counterpart.price} USD ")
            
        elif order.type == 'sell':

            #give me the amount i sold for
            self.profile.wallet['usd_balance'] += delta_filled_order * order.amount * order.price
            print(f" i get {delta_filled_order * order.amount * order.price} USD")
            # give the counterpart what he bought
            profile_counterpart.wallet['btc_balance'] += delta_filled_counterpart * counterpart.amount
            print(f" the counterpart gets the {delta_filled_counterpart * counterpart.amount} BTC he bought")
            #give back the counterpart the unspent money ( if my selling price is lower than their offer )
            profile_counterpart.wallet['usd_balance'] += delta_filled_counterpart * counterpart.amount * (counterpart.price - order.price)
            print(f" the counterpart gets back the {delta_filled_counterpart * counterpart.amount * ( counterpart.price - order.price)} USD of unspent money")

        #saving the changes
        self.profile.save()
        profile_counterpart.save()

    ''' load content of buy order book '''
    def load_tables_data_buy(self):

            # get open buy orders
            open_buy_orders = Order.objects.filter(type='buy').exclude(filled=True).order_by('price')
            self.buy_orders_table.setRowCount(len(open_buy_orders))

            # each order fills a row of the table
            for row, order in enumerate(open_buy_orders):
                self.buy_orders_table.setItem(row, 0, QTableWidgetItem(str(order.amount * (1 - order.quote_filled))))
                self.buy_orders_table.setItem(row, 1, QTableWidgetItem(str(order.price)))
                self.buy_orders_table.setItem(row, 2, QTableWidgetItem(str((order.amount * order.price) * (1 - order.quote_filled))))
                self.buy_orders_table.setItem(row, 3, QTableWidgetItem(order.user))
    
    ''' laod content of sell order book '''
    def load_tables_data_sell(self):
        
        # get open sell orders
        open_sell_orders = Order.objects.filter(type='sell').exclude(filled=True).order_by('price')
        self.sell_orders_table.setRowCount(len(open_sell_orders))

        # each order fills a row of the table
        for row, order in enumerate(open_sell_orders):
            self.sell_orders_table.setItem(row, 0, QTableWidgetItem(str(order.amount * (1 - order.quote_filled))))
            self.sell_orders_table.setItem(row, 1, QTableWidgetItem(str(order.price)))
            self.sell_orders_table.setItem(row, 2, QTableWidgetItem(str((order.amount * order.price) * (1 - order.quote_filled))))
            self.sell_orders_table.setItem(row, 3, QTableWidgetItem(order.user))

    ''' load my open orders table '''
    def load_my_open_orders_table(self):

        # get my open orders
        my_open_orders = Order.objects.filter(user=self.profile.user.username).exclude(filled=True).order_by('date_created')
        self.my_open_orders_table.setRowCount(len(my_open_orders))

        # each order fills a row of the table
        for row, order in enumerate(my_open_orders):
            self.my_open_orders_table.setItem(row, 0, QTableWidgetItem(order.type))
            self.my_open_orders_table.setItem(row, 1, QTableWidgetItem(str(order.amount)))
            self.my_open_orders_table.setItem(row, 2, QTableWidgetItem(str(order.price)))
            self.my_open_orders_table.setItem(row, 3, QTableWidgetItem(str(order.quote_filled)))

    ''' load my exchange history (filled orders) '''
    def load_personal_history_table(self):

        # get my filled orders
        my_filled_orders = Order.objects.filter(user=self.profile.user.username, filled=True).order_by('date_created')
        self.my_order_history_table.setRowCount(len(my_filled_orders))

        # each order fills a row of the table
        for row, order in enumerate(my_filled_orders):
            self.my_order_history_table.setItem(row, 0, QTableWidgetItem(str(order.date_filled)))
            self.my_order_history_table.setItem(row, 1, QTableWidgetItem(order.type))
            self.my_order_history_table.setItem(row, 2, QTableWidgetItem(str(order.price)))
            self.my_order_history_table.setItem(row, 3, QTableWidgetItem(str(order.amount)))
    
    ''' displays current balance of USD and BTC in wallet tab'''
    def display_wallet_balances(self):

        self.user_btc_balance.display(self.profile.wallet['btc_balance'])
        self.user_usd_balance.display(self.profile.wallet['usd_balance'])

    ''' displays current BTC and USD net profit in P/L tab'''
    def display_net_profit(self):

        btc_profit = self.profile.wallet['btc_balance'] - self.profile.wallet['starting_btc_balance']
        usd_profit = self.profile.wallet['usd_balance'] # every user starts with 0 USD

        self.net_btc_profit.display(btc_profit)
        self.net_usd_profit.display(usd_profit)

    ''' updates to current data inside database '''
    def update_interface(self):
        
        # update plot
        self.plot()

        # update order book 
        self.load_tables_data_buy()
        self.load_tables_data_sell()

        # update my open orders table
        self.load_my_open_orders_table()

        # update order history table
        self.load_personal_history_table()

        # update profit/loss
        self.display_net_profit()

        # update wallet balances
        self.display_wallet_balances()