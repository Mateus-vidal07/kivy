from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.core.window import Window

from kivymd.theming import ThemeManager
from kivymd.pickers import MDDatePicker
from kivymd.dialog import MDDialog
from kivymd.cards import MDCardPost
from kivymd.snackbars import Snackbar
import sqlite3
import os

#creating a database ########################
def connect_to_database(path):
	try:
		con = sqlite3.connect(path)
		cursor = con.cursor()
		create_table_products(cursor)
		create_user(cursor)
		con.commit()
		con.close()
	except Exception  as e:
		print(e)
		
#creating products table ##########################
def create_table_products(cursor):
	cursor.execute('''
		CREATE TABLE IF NOT EXISTS products(
		ID INTEGER PRIMARY KEY AUTOINCREMENT,
		Dono 	TEXT NOT NULL,
		Marca 	TEXT NOT NULL,
		Defeito TEXT NOT NULL,
		Preco 	FLOAT NOT NULL,
		Data_in INT NOT NULL,
		Data_out INT NOT NULL
		)'''
	)
#create user table #####################################
def create_user(cursor):
	cursor.execute(''' 
		CREATE TABLE IF NOT EXISTS user (
		Usuario TEXT NOT NULL,
		Email TEXT NOT NULL,
		Senha TEXT NOT NULL,
		Data INT NOT NULL
		)
	
	''')
	
class MainWid(ScreenManager):
	def __init__(self, **kwargs):
		super(MainWid, self).__init__(**kwargs)
		self.APP_PATH = os.getcwd()
		self.DB_PATH = self.APP_PATH+'/my_database.db'
		self.startwid = BoxLayout()
		self.registerwid = BoxLayout()
		self.list_item = ListItem(self)
		self.insert = BoxLayout()
		self.update_data = BoxLayout()
		
		#add startScren
		wid = Screen(name = 'start')
		wid.add_widget(self.startwid)
		self.add_widget(wid)
		#add resgister screen
		wid = Screen(name = 'register')
		wid.add_widget(self.registerwid)
		self.add_widget(wid)
		#add ListItem screen
		wid = Screen(name='list_item')
		wid.add_widget(self.list_item)
		self.add_widget(wid)
		#add InsertData screen
		wid = Screen(name='insert_data')
		wid.add_widget(self.insert)
		self.add_widget(wid)
		#add UpdateData screen
		wid = Screen(name='update')
		wid.add_widget(self.update_data)
		self.add_widget(wid)
		
		self.goto_start()
		
	#functions changes screens
	def goto_start(self):
		self.startwid.clear_widgets()
		wid = StartWid(self)
		self.startwid.add_widget(wid)
		self.current = 'start'
		
	def goto_register(self):
		self.registerwid.clear_widgets()
		wid = RegisterWid(self)
		self.registerwid.add_widget(wid)
		self.current = 'register'
		
	def goto_list_item(self):
		self.list_item.check_memory()
		self.current = 'list_item'
	
	def goto_insert_data(self):
		self.insert.clear_widgets()
		wid = InsertData(self)
		self.insert.add_widget(wid)
		self.current = 'insert_data'
		
	def goto_update(self, data_id):
		self.update_data.clear_widgets()
		wid = UpdateData(self, data_id)
		self.update_data.add_widget(wid)
		self.current = 'update'

class StartWid(BoxLayout):
	def __init__(self, mainwid, **kwargs):
		super(StartWid, self).__init__(**kwargs)
		self.mainwid = mainwid
		self.ids.user_field.ids.field.on_text_validate = True
		connect_to_database(self.mainwid.DB_PATH)
		
	def close_dialog(self, *args):
		pass
		
	def login(self):
		con = sqlite3.connect(self.mainwid.DB_PATH)
		cursor = con.cursor()
		d1 = self.ids.user_field.text
		d2 = self.ids.pwd_field.text
		a1 = (d1, d2)
		s1 = 'SELECT * FROM user WHERE Usuario = ? and Senha = ?'
		
		cursor.execute(s1, a1)
		result = cursor.fetchall()
		if result:
			self.mainwid.transition.direction = 'left'
			self.mainwid.goto_list_item()
		else:
			dialog = MDDialog(
            title='Oops', size_hint=(.8, .3),
            text="[color=#FF0000] Usuario ou Senha Invalido [/color]", events_callback = self.close_dialog)
			dialog.open()
			
	
	def create_user(self):
		self.mainwid.transition.direction = 'left'
		self.mainwid.goto_register()

class RegisterWid(BoxLayout):
	def __init__(self, mainwid, **kwargs):
		super(RegisterWid, self).__init__(**kwargs)
		self.mainwid = mainwid
		
	def show_date_picker(self, *args):
		MDDatePicker(self.set_previous_date).open()
		
	def set_previous_date(self, date_obj):
		self.previous_date = date_obj
		self.ids.calendar_field.text = str(date_obj)
		
	def dialogs(self):
		dialog = MDDialog(
		title = 'Concluido', size_hint=(.8, .3),
		text = 'Parabens sua conta foi criada com sucesso', events_callback = self.close_dialog)
		dialog.open()
	def close_dialog(self, *args):
		pass
		
	def add_user(self):
		con = sqlite3.connect(self.mainwid.DB_PATH)
		cursor = con.cursor()
		d1 = self.ids.usr_field.text
		d2 = self.ids.email_field.text
		d3 = self.ids.pwd_field.text
		d4 = self.ids.calendar_field.text
		a1 = (d1, d2, d3, d4)
		s1 = 'INSERT INTO user(Usuario, Email, Senha, Data)'
		s2 = 'VALUES("%s", "%s", "%s", %s)' % a1
		
		try:
			cursor.execute(s1+' '+s2)
			con.commit()
			con.close()
			self.mainwid.transition.direction = 'right'
			self.mainwid.goto_start()
			self.dialogs()
		except Exception as e:
			dialog = MDDialog(
			title = 'Oops', size_hint=(.8, .4),
			text = 'Certifique-se que os dados fornecidos estao corretos', events_callback = self.close_dialog)
			dialog.open()
			con.close()
			
	def back_screen(self):
		self.mainwid.transition.direction = 'right'
		self.mainwid.goto_start()

class ListItem(BoxLayout):
	def __init__(self, mainwid, **kwargs):
		super(ListItem, self).__init__(**kwargs)
		self.mainwid = mainwid
		#self.data_id = data_id
	
	def check_memory(self):
		self.ids.container.clear_widgets()
		con = sqlite3.connect(self.mainwid.DB_PATH)
		cursor = con.cursor()
		cursor.execute('select ID, Dono, Marca, Defeito, Preco, Data_in, Data_out from products')
		
		def callback_for_menu_items(text_item):
			data_id = text_item.split(' ')[1]
			print(len(text_item))
			self.mainwid.transition.direction = 'left'
			self.mainwid.goto_update(data_id)

		for i in cursor:
			
			menu_items = [{
			'viewclass': 'MDMenuItem',
			'text': 'Editar {}'.format(str(i[0])),
			'callback': callback_for_menu_items
		}]
			
			data_id = str(i[0])
			r1 = 'ID: '+ data_id +'\n'
			r2 = '[b]Dono:[/b] '+i[1]+ '      '+'[b]Marca: [/b]'+i[2]+ '      '+'[b]Preco:[/b] R$'+str(i[4])+'\n''\n'
			r3 = '[b]Defeito:[/b] '+i[3]
			
			self.ids.container.add_widget(MDCardPost(right_menu = menu_items, name_data = 'Manutencao de celulares\n'+str(i[5]), text_post=r1+r2+r3, swipe=True, path_to_avatar = 'myimage.png'))
			
	def add_item(self):
		self.mainwid.transition.direction = 'left'
		self.mainwid.goto_insert_data()
	def logout_screen(self):
		self.mainwid.goto_start()

class InsertData(BoxLayout):
	def __init__(self, mainwid, **kwargs):
		super(InsertData, self).__init__(**kwargs)
		self.mainwid = mainwid
		
	def close_dialog(sel, *args):
		pass
	
	def insert_data(self):
		con = sqlite3.connect(self.mainwid.DB_PATH)
		cursor = con.cursor()
		d1 = self.ids.dono.text
		d2 = self.ids.marca.text
		d3 = self.ids.defeito.text
		d4 = self.ids.preco.text
		d5 = self.ids.data_in.text
		d6 = self.ids.data_out.text
		a1 = (d1, d2, d3, d4, d5, d6)
		s1 = 'INSERT INTO products(Dono, Marca, Defeito, Preco, Data_in, Data_out)'
		s2 = 'VALUES("%s", "%s", "%s", %s, "%s", "%s")' % a1
		
		try:
			cursor.execute(s1+' '+s2)
			con.commit()
			con.close()
			self.mainwid.transition.direction = 'right'
			self.mainwid.goto_list_item()
			self.show_snackbar()
		except Exception as e:
			dialog = MDDialog(
			title = 'Oops', size_hint=(.8, .4),
			text = 'Certifique-se que os dados fornecidos estao corretos', events_callback = self.close_dialog)
			dialog.open()
			con.close()
	
	def back_screen(self):
		self.mainwid.transition.direction = 'right'
		self.mainwid.goto_list_item()
	
	def close(self):
		pass		
	def show_snackbar(self):
		 Snackbar(text="Item adicionado com sucesso!").show()
	
class UpdateData(BoxLayout):
	def __init__(self, mainwid, data_id, **kwargs):
		super(UpdateData, self).__init__(**kwargs)
		self.mainwid = mainwid
		self.data_id = data_id
		self.check_data()
		
	def check_data(self):
		con = sqlite3.connect(self.mainwid.DB_PATH)
		cursor = con.cursor()
		s = 'SELECT Dono, Marca, Defeito, Preco, Data_in, Data_out FROM products WHERE ID='
		cursor.execute(s+self.data_id)
		for i in cursor:
			self.ids.dono.text = i[0]
			self.ids.marca.text = i[1]
			self.ids.defeito.text = i[2]
			self.ids.preco.text = str(i[3])
			self.ids.data_in.text = str(i[4])
			self.ids.data_out.text = str(i[5])
		con.close()
	def change_data(self):
		con = sqlite3.connect(self.mainwid.DB_PATH)
		cursor = con.cursor()
		d1 = self.ids.dono.text
		d2 = self.ids.marca.text
		d3 = self.ids.defeito.text
		d4 = self.ids.preco.text
		d5 = self.ids.data_in.text
		d6 = self.ids.data_out.text
		a1 = (d1, d2, d3, d4, d5, d6)
		s1 = 'UPDATE products SET'
		s2 = 'Dono="%s", Marca="%s", Defeito="%s", Preco=%s, Data_in="%s", Data_out="%s"' % a1
		s3 = 'WHERE ID=%s' % self.data_id
		try:
			cursor.execute(s1+' '+s2+' '+s3)
			con.commit()
			con.close()
			self.mainwid.transition.direction = 'right'
			self.mainwid.goto_list_item()
			self.show_snackbar()
		except Exception as  e:
			dialog = MDDialog(
			title = 'Oops', size_hint=(.8, .4),
			text = 'Certifique-se que os dados fornecidos estao corretos', events_callback = self.close_dialog)
			dialog.open()
			con.close()
		
	def delete_data(self):
		con = sqlite3.connect(self.mainwid.DB_PATH)
		cursor = con.cursor()
		s = 'DELETE FROM products WHERE ID='+ self.data_id
		cursor.execute(s)
		con.commit()
		con.close()
		self.mainwid.transition.direction = 'right'
		self.mainwid.goto_list_item()
	
	def back_screen(self):
		self.mainwid.transition.direction = 'right'
		self.mainwid.goto_list_item()
		
	#snackbar
	def show_snackbar(self):
		Snackbar(text='Item atualizado com sucesso!').show()
	def close_dialog(self, *args):
		pass
	
class MainApp(App):
	theme_cls = ThemeManager()
	title = "inventario"
	previous_date = ''
	
	def build(self):
		return MainWid()
		
	
		
if __name__ == "__main__":
	Window.size = (440, 620)
	MainApp().run()
