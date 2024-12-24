#!/usr/bin/env python3
import gi
import subprocess
import os
import logging
import sys
from pathlib import Path

# Create a log file in the user's home directory
log_file = str(Path.home() / '.hotspot-indicator.log')

# Logging configuration
logging.basicConfig(
    filename=log_file,
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

gi.require_version('Gtk', '3.0')
gi.require_version('AppIndicator3', '0.1')
gi.require_version('Notify', '0.7')
from gi.repository import Gtk, AppIndicator3, Notify, GLib

class Language:
    def __init__(self):
        """Dil sınıfı, uygulamanın dilini ve metin çevirilerini yönetir."""
        self.current_lang = 'tr'  # Varsayılan dil
        self.translations = {
            'tr': {
                'window_title': 'Hotspot Shield VPN',
                'status': 'Durum',
                'connect': 'Bağlan',
                'disconnect': 'Bağlantıyı Kes',
                'locations': 'Konumlar',
                'quit': 'Çıkış',
                'show_interface': 'Arayüzü Göster',
                'status_check': 'Durum Kontrolü',
                'connected': 'BAĞLI',
                'not_connected': 'BAĞLI DEĞİL',
                'login': 'Giriş Yap',
                'logout': 'Hesaptan Çıkış',
                'username': 'Kullanıcı Adı',
                'password': 'Şifre',
                'login_button': 'Giriş',
                'cancel': 'İptal',
                'account_status': 'Hesap Durumu',
                'connection_failed': 'Bağlantı Başarısız',
                'connection_error': 'Bağlantı Hatası',
                'login_failed': 'Giriş Başarısız Oldu',
                'logged_out': 'Çıkış Yapıldı',
                'connecting': 'Bağlanılıyor...',
                'disconnecting': 'Bağlantı Kesiliyor...',
                'error': 'Hata',
                'vpn_connection': 'VPN Bağlantısı',
                'not_signed_in': 'Oturum Açılmadı. Giriş Yapılıyor...',
                'logout_failed': 'Çıkış Başarısız Oldu',
                'disconnect_error': 'Bağlantı Kesme Hatası',
                'not_available': 'Mevcut Değil',
                'no_internet': 'İnternet Bağlantısı Yok',
                'no_internet_message': 'İnternet bağlantısı bulunamadı. Lütfen bağlantınızı kontrol edip tekrar deneyin.',
                'connecting_location': 'Konuma Bağlanılıyor...',
                'connection_successful': 'Bağlantı Başarılı',
                'connection_failed_try_again': 'Bağlantı başarısız. Tekrar deneyin.',
                'checking_connection': 'Bağlantı kontrol ediliyor...'
            },
            'en': {
                'window_title': 'Hotspot Shield VPN',
                'status': 'Status',
                'connect': 'Connect',
                'disconnect': 'Disconnect',
                'locations': 'Locations',
                'quit': 'Quit',
                'show_interface': 'Show Interface',
                'status_check': 'Status Check',
                'connected': 'CONNECTED',
                'not_connected': 'NOT CONNECTED',
                'login': 'Login',
                'logout': 'Logout',
                'username': 'Username',
                'password': 'Password',
                'login_button': 'Login',
                'cancel': 'Cancel',
                'account_status': 'Account Status',
                'connection_failed': 'Connection Failed',
                'connection_error': 'Connection Error',
                'login_failed': 'Login Failed',
                'logged_out': 'Logged Out',
                'connecting': 'Connecting...',
                'disconnecting': 'Disconnecting...',
                'error': 'Error',
                'vpn_connection': 'VPN Connection',
                'not_signed_in': 'Not Signed In. Logging In...',
                'logout_failed': 'Logout Failed',
                'disconnect_error': 'Disconnect Error',
                'not_available': 'Not Available',
                'no_internet': 'No Internet Connection',
                'no_internet_message': 'No internet connection found. Please check your connection and try again.',
                'connecting_location': 'Connecting to Location...',
                'connection_successful': 'Connection Successful',
                'connection_failed_try_again': 'Connection failed. Please try again.',
                'checking_connection': 'Checking connection...'
            }
        }

    def get_text(self, key):
        """Belirtilen anahtar için çeviri metnini döndürür."""
        return self.translations[self.current_lang].get(key, key)

    def switch_language(self):
        """Uygulama dilini değiştirir."""
        self.current_lang = 'en' if self.current_lang == 'tr' else 'tr'

class HotspotShieldApp:
    def check_internet_connection(self):
        """İnternet bağlantısını kontrol eder."""
        try:
            # 1.1.1.1 (Cloudflare DNS) ping atarak internet kontrolü
            result = subprocess.run(
                ['ping', '-c', '1', '1.1.1.1'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=5  # 5 saniye timeout
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, subprocess.SubprocessError):
            return False

    def __init__(self):
        """Uygulamanın ana sınıfı, GUI ve işlevselliği yönetir."""
        self.lang = Language()

        # İnternet bağlantısını kontrol et
        if not self.check_internet_connection():
            dialog = Gtk.MessageDialog(
                parent=None,
                flags=0,
                message_type=Gtk.MessageType.ERROR,
                buttons=Gtk.ButtonsType.OK,
                text=self.lang.get_text('no_internet')
            )
            dialog.format_secondary_text(self.lang.get_text('no_internet_message'))
            dialog.run()
            dialog.destroy()
            sys.exit(1)

        # Create the main window
        self.window = Gtk.Window(title=self.lang.get_text('window_title'))
        self.window.set_border_width(10)
        self.window.set_default_size(400, 500)
        self.window.set_position(Gtk.WindowPosition.CENTER)
        self.window.connect("delete-event", self.on_window_close)

        # Initialize Notify
        if not Notify.is_initted():
            Notify.init("Hotspot Shield VPN")

        # Set up the system tray indicator
        self.indicator = AppIndicator3.Indicator.new(
            "hotspot-shield",
            "network-vpn",
            AppIndicator3.IndicatorCategory.APPLICATION_STATUS
        )
        self.indicator.set_status(AppIndicator3.IndicatorStatus.ACTIVE)
        self.indicator.set_menu(self.build_tray_menu())

        # Create the main UI
        self.create_main_ui()

        # Attempt to connect automatically
        self.auto_connect()

    def on_window_close(self, window, event):
        """Pencere kapatma olayını yönetir."""
        try:
            window.hide()  # Pencereyi gizle
            return True  # True döndürerek pencerenin tamamen kapanmasını engelle
        except Exception as e:
            logging.error(f"Window close error: {str(e)}")
            return False

    def show_window(self, _):
        """Ana pencereyi gösterir."""
        try:
            self.window.show_all()
            self.window.present()  # Pencereyi öne getir
        except Exception as e:
            logging.error(f"Show window error: {str(e)}")

    def auto_connect(self):
        """Uygulama başladığında otomatik olarak bağlanmaya çalışır."""
        try:
            # Direkt bağlanmayı dene
            result = subprocess.run(
                ['hotspotshield', 'connect'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=False
            )
            # Eğer giriş yapılmamışsa
            if 'not signed in' in result.stderr.lower() or 'not signed in' in result.stdout.lower():
                if self.show_login_dialog():
                    self.connect_vpn()
                else:
                    sys.exit(1)
            else:
                # Bağlantı başarılı mı kontrol et
                import time
                time.sleep(2)
                if self.is_connected():
                    self.show_notification(
                        self.lang.get_text('vpn_connection'),
                        self.lang.get_text('connection_successful')
                    )
                    self.update_status_display()
                else:
                    self.connect_vpn()
        except Exception as e:
            logging.error(f"Auto connect error: {str(e)}")
            if self.show_login_dialog():
                self.connect_vpn()

    def create_main_ui(self):
        """Ana kullanıcı arayüzünü oluşturur."""
        # Main container
        self.main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.window.add(self.main_box)

        # Header with logo and title
        self.header_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        self.logo = Gtk.Image()
        self.logo.set_from_icon_name("network-vpn", Gtk.IconSize.DIALOG)
        self.header_box.pack_start(self.logo, True, True, 0)
        self.title_label = Gtk.Label()
        self.title_label.set_markup("<span size='x-large'><b>Hotspot Shield VPN</b></span>")
        self.header_box.pack_start(self.title_label, True, True, 0)
        self.main_box.pack_start(self.header_box, False, True, 10)

        # Status display
        self.status_frame = Gtk.Frame(label=self.lang.get_text('status'))
        self.status_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        self.status_frame.add(self.status_box)
        self.status_label = Gtk.Label()
        self.status_label.set_markup(f"<span>{self.lang.get_text('checking_connection')}</span>")
        self.status_box.pack_start(self.status_label, True, True, 5)
        self.main_box.pack_start(self.status_frame, False, True, 0)

        # Action buttons
        self.button_box = Gtk.Box(spacing=6)
        self.connect_button = Gtk.Button(label=self.lang.get_text('connect'))
        self.connect_button.connect("clicked", self.on_connect_clicked)
        self.button_box.pack_start(self.connect_button, True, True, 0)
        self.disconnect_button = Gtk.Button(label=self.lang.get_text('disconnect'))
        self.disconnect_button.connect("clicked", self.on_disconnect_clicked)
        self.button_box.pack_start(self.disconnect_button, True, True, 0)
        self.main_box.pack_start(self.button_box, False, True, 0)

        # Locations list
        self.locations_frame = Gtk.Frame(label=self.lang.get_text('locations'))
        self.locations_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        self.locations_frame.add(self.locations_box)
        self.locations_list = Gtk.ListBox()
        self.locations_list.set_selection_mode(Gtk.SelectionMode.SINGLE)
        self.locations_list.connect('row-activated', self.on_location_selected)
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scrolled.add(self.locations_list)
        self.locations_box.pack_start(scrolled, True, True, 0)
        self.main_box.pack_start(self.locations_frame, True, True, 0)

        # Footer with language switch and link
        self.main_box.pack_start(self.create_footer(), False, False, 10)

        # Load locations and update status
        self.load_locations()
        self.update_status_display()

    def create_footer(self):
        """Alt bilgi bölümünü oluşturur."""
        footer_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        # Link button
        link_button = Gtk.LinkButton.new_with_label(
            "https://furkanyildirim.com",
            "furkanyildirim.com"
        )
        # Language switch button
        lang_button = Gtk.Button(label="EN/TR")
        lang_button.connect("clicked", self.switch_language)
        footer_box.pack_start(link_button, False, False, 0)
        footer_box.pack_start(lang_button, False, False, 0)
        return footer_box

    def build_tray_menu(self):
        """Sistem tepsisi menüsünü oluşturur."""
        menu = Gtk.Menu()

        # Connection status display
        connection_status = Gtk.MenuItem(label=f"{self.lang.get_text('status')}: {self.get_connection_status_text()}")
        connection_status.set_sensitive(False)
        menu.append(connection_status)
        menu.append(Gtk.SeparatorMenuItem())

        show_item = Gtk.MenuItem(label=self.lang.get_text('show_interface'))
        show_item.connect('activate', self.show_window)
        menu.append(show_item)
        menu.append(Gtk.SeparatorMenuItem())

        status_item = Gtk.MenuItem(label=self.lang.get_text('status_check'))
        status_item.connect('activate', self.check_status)
        menu.append(status_item)
        menu.append(Gtk.SeparatorMenuItem())

        connect_item = Gtk.MenuItem(label=self.lang.get_text('connect'))
        connect_item.connect('activate', self.on_connect_clicked)
        connect_item.set_sensitive(not self.is_connected())
        menu.append(connect_item)

        disconnect_item = Gtk.MenuItem(label=self.lang.get_text('disconnect'))
        disconnect_item.connect('activate', self.on_disconnect_clicked)
        disconnect_item.set_sensitive(self.is_connected())
        menu.append(disconnect_item)

        menu.append(Gtk.SeparatorMenuItem())

        quit_item = Gtk.MenuItem(label=self.lang.get_text('quit'))
        quit_item.connect('activate', self.quit)
        menu.append(quit_item)

        menu.show_all()
        return menu

    def get_connection_status_text(self):
        """Bağlantı durum metnini alır."""
        return self.lang.get_text('connected') if self.is_connected() else self.lang.get_text('not_connected')

    def check_status(self, widget=None):
        """VPN durumunu kontrol eder."""
        self.update_status_display()

    def on_connect_clicked(self, widget):
        """Bağlan düğmesine tıklandığında çağrılır."""
        self.connect_vpn()

    def on_disconnect_clicked(self, widget):
        """Bağlantıyı kes düğmesine tıklandığında çağrılır."""
        self.disconnect_vpn()

    def switch_language(self, widget=None):
        """Uygulama dilini değiştirir."""
        try:
            # Dili değiştir
            self.lang.switch_language()
            # UI güncellemesini ana thread'den yap
            GLib.idle_add(self._update_ui_texts_safe)
        except Exception as e:
            logging.error(f"Language switch error: {str(e)}")
            self.show_error_message(
                "Hata/Error",
                "Dil değiştirme sırasında bir hata oluştu.\nAn error occurred while switching language."
            )

    def _update_ui_texts_safe(self):
        """UI öğelerini güvenli bir şekilde günceller."""
        try:
            # Önce mevcut menüyü temizle
            self.indicator.set_menu(None)
            # Window ve label'ları güncelle
            self.window.set_title(self.lang.get_text('window_title'))
            self.connect_button.set_label(self.lang.get_text('connect'))
            self.disconnect_button.set_label(self.lang.get_text('disconnect'))
            self.status_frame.set_label(self.lang.get_text('status'))
            self.locations_frame.set_label(self.lang.get_text('locations'))
            self.title_label.set_markup(
                f"<span size='x-large'><b>{self.lang.get_text('window_title')}</b></span>"
            )
            # Yeni menüyü oluştur
            new_menu = self.build_tray_menu()
            self.indicator.set_menu(new_menu)
            # Durumu güncelle
            self.update_status_display()
            return False  # GLib.idle_add için False döndür
        except Exception as e:
            logging.error(f"Safe UI update error: {str(e)}")
            return False

    def load_locations(self):
        """VPN konumlarını listeye yükler."""
        try:
            locations_output = subprocess.check_output(['hotspotshield', 'locations']).decode()
            locations = locations_output.strip().split('\n')
            # İlk iki satırı atla ve boş olmayan satırları al
            filtered_locations = [loc for loc in locations[2:] if loc.strip()]
            for location in filtered_locations:
                if location.strip():
                    row = Gtk.ListBoxRow()
                    hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
                    row.add(hbox)
                    label = Gtk.Label(label=location, xalign=0)
                    hbox.pack_start(label, True, True, 0)
                    self.locations_list.add(row)
        except Exception as e:
            logging.error(f"Locations loading error: {str(e)}")
            row = Gtk.ListBoxRow()
            label = Gtk.Label(label=self.lang.get_text('locations') + ' ' +
                              self.lang.get_text('not_available'), xalign=0)
            row.add(label)
            self.locations_list.add(row)

    def connect_vpn(self):
        """VPN'e bağlanmayı dener."""
        try:
            # İnternet bağlantısını kontrol et
            if not self.check_internet_connection():
                self.show_error_message(
                    self.lang.get_text('no_internet'),
                    self.lang.get_text('no_internet_message')
                )
                return False

            # Bağlantı durumunu kontrol et
            if self.is_connected():
                logging.info("Already connected, skipping connection attempt")
                self.update_status_display()
                return True

            # Bağlanma işlemini başlat
            self.status_label.set_markup(f"<span>{self.lang.get_text('connecting')}</span>")
            self.connect_button.set_sensitive(False)
            self.disconnect_button.set_sensitive(False)
            while Gtk.events_pending():
                Gtk.main_iteration()

            result = subprocess.run(
                ['hotspotshield', 'connect'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=False
            )

            # Bağlantı sonucunu kontrol et
            if result.returncode == 0:
                import time
                time.sleep(2)  # Bağlantının kurulmasını bekle
                if self.is_connected():
                    self.show_notification(
                        self.lang.get_text('vpn_connection'),
                        self.lang.get_text('connection_successful')
                    )
                    self.update_status_display()
                    return True

            # Bağlantı başarısız olduysa
            if 'not signed in' in result.stderr.lower():
                self.show_notification(
                    self.lang.get_text('vpn_connection'),
                    self.lang.get_text('not_signed_in')
                )
                if self.show_login_dialog():
                    return self.connect_vpn()
            else:
                self.show_error_message(
                    self.lang.get_text('connection_error'),
                    self.lang.get_text('connection_failed_try_again')
                )

            self.update_status_display()
            return False
        except Exception as e:
            logging.error(f"Connect error: {str(e)}")
            self.show_error_message(
                self.lang.get_text('error'),
                self.lang.get_text('connection_failed')
            )
            self.update_status_display()
            return False

    def disconnect_vpn(self):
        """VPN bağlantısını keser."""
        try:
            # Bağlantı durumunu kontrol et
            if not self.is_connected():
                logging.info("Already disconnected, skipping disconnection attempt")
                self.update_status_display()
                return True

            # Bağlantı kesme işlemini başlat
            self.status_label.set_markup(f"<span>{self.lang.get_text('disconnecting')}</span>")
            self.connect_button.set_sensitive(False)
            self.disconnect_button.set_sensitive(False)
            while Gtk.events_pending():
                Gtk.main_iteration()

            # 'hotspotshield disconnect' komutunu çalıştır
            result = subprocess.run(
                ['hotspotshield', 'disconnect'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=30  # 30 saniye timeout
            )

            # Kısa bir bekleme süresi
            import time
            time.sleep(2)

            # Bağlantının kesilip kesilmediğini kontrol et
            if not self.is_connected():
                self.show_notification(
                    self.lang.get_text('vpn_connection'),
                    self.lang.get_text('not_connected')
                )
                self.update_status_display()
                return True
            else:
                logging.error("Disconnect command executed but VPN is still connected.")
                self.show_error_message(
                    self.lang.get_text('disconnect_error'),
                    self.lang.get_text('disconnect_error')
                )
                self.update_status_display()
                return False
        except subprocess.TimeoutExpired:
            logging.error("Disconnect command timed out.")
            self.show_error_message(
                self.lang.get_text('disconnect_error'),
                self.lang.get_text('disconnect_error')
            )
            self.update_status_display()
            return False
        except Exception as e:
            logging.error(f"Disconnect error: {str(e)}")
            self.show_error_message(
                self.lang.get_text('error'),
                self.lang.get_text('disconnect_error')
            )
            self.update_status_display()
            return False

    def connect_to_location(self, widget, location):
        """Belirli bir VPN konumuna bağlanır."""
        try:
            # İnternet bağlantısını kontrol et
            if not self.check_internet_connection():
                self.show_error_message(
                    self.lang.get_text('no_internet'),
                    self.lang.get_text('no_internet_message')
                )
                return False

            # Bağlantı durumunu güncelle
            self.status_label.set_markup(
                f"<span>{self.lang.get_text('connecting_location')} {location}...</span>"
            )
            self.connect_button.set_sensitive(False)
            self.disconnect_button.set_sensitive(False)
            while Gtk.events_pending():
                Gtk.main_iteration()

            # Önce mevcut bağlantıyı kes
            if self.is_connected():
                self.disconnect_vpn()

            # Yeni konuma bağlan
            result = subprocess.run(
                ['hotspotshield', 'connect', location],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=False
            )

            # Bağlantı sonucunu kontrol et
            if result.returncode == 0:
                import time
                time.sleep(3)  # Bağlantının kurulmasını bekle
                if self.is_connected():
                    self.show_notification(
                        self.lang.get_text('vpn_connection'),
                        f"{location} {self.lang.get_text('connected')}"
                    )
                    self.update_status_display()
                    return True

            self.show_error_message(
                self.lang.get_text('error'),
                self.lang.get_text('connection_failed_try_again')
            )
            self.update_status_display()
            return False
        except Exception as e:
            logging.error(f"Location connect error: {str(e)}")
            self.show_error_message(
                self.lang.get_text('error'),
                self.lang.get_text('connection_failed')
            )
            self.update_status_display()
            return False

    def on_location_selected(self, listbox, row):
        """Listeden bir konum seçildiğinde çağrılır."""
        try:
            location = row.get_children()[0].get_children()[0].get_text().split()[0]
            self.connect_to_location(None, location)
        except Exception as e:
            logging.error(f"Location selection error: {str(e)}")

    def show_login_dialog(self):
        """Giriş iletişim kutusunu gösterir."""
        dialog = Gtk.Dialog(
            title=self.lang.get_text('login'),
            parent=self.window,
            flags=0
        )
        dialog.add_buttons(
            self.lang.get_text('cancel'),
            Gtk.ResponseType.CANCEL,
            self.lang.get_text('login_button'),
            Gtk.ResponseType.OK
        )
        box = dialog.get_content_area()
        grid = Gtk.Grid()
        grid.set_row_spacing(10)
        grid.set_column_spacing(10)
        box.add(grid)

        username_label = Gtk.Label(label=self.lang.get_text('username'))
        username_entry = Gtk.Entry()
        grid.attach(username_label, 0, 0, 1, 1)
        grid.attach(username_entry, 1, 0, 1, 1)

        password_label = Gtk.Label(label=self.lang.get_text('password'))
        password_entry = Gtk.Entry()
        password_entry.set_visibility(False)
        grid.attach(password_label, 0, 1, 1, 1)
        grid.attach(password_entry, 1, 1, 1, 1)

        dialog.show_all()
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            username = username_entry.get_text()
            password = password_entry.get_text()
            success = self.login_to_hotspot(username, password)
            dialog.destroy()
            if not success:
                self.show_error_message(
                    self.lang.get_text('login_failed'),
                    self.lang.get_text('connection_failed')
                )
                return self.show_login_dialog()  # Başarısızsa tekrar göster
            return success
        dialog.destroy()
        return False

    def login_to_hotspot(self, username, password):
        """Hotspot Shield hesabına giriş yapmayı dener."""
        try:
            # Önce mevcut oturumu kontrol et ve gerekirse çıkış yap
            subprocess.run(
                ['hotspotshield', 'account', 'signout'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False
            )
            # Giriş komutunu çalıştır
            login_process = subprocess.Popen(
                ['hotspotshield', 'account', 'signin'],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            # Kullanıcı adı ve şifreyi gönder
            stdout, stderr = login_process.communicate(input=f"{username}\n{password}\n")
            # Giriş durumunu kontrol et
            status_check = subprocess.run(
                ['hotspotshield', 'account', 'status'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=False
            )
            # Eğer çıktıda e-posta adresi varsa giriş başarılıdır
            if username.lower() in status_check.stdout.lower():
                logging.info("Login successful")
                logging.info(f"Account status: {status_check.stdout}")
                return True
            # Hata durumunda log kaydet
            logging.error(f"Login failed. Status output: {status_check.stdout}")
            logging.error(f"Login stderr: {status_check.stderr}")
            return False
        except Exception as e:
            logging.error(f"Login exception: {str(e)}")
            return False

    def check_login_status(self):
        """Kullanıcının oturum açıp açmadığını kontrol eder."""
        try:
            # Direkt bağlantı denemesi yap
            result = subprocess.run(
                ['hotspotshield', 'connect'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=False
            )
            # Eğer "not signed in" mesajı varsa False döndür
            if 'not signed in' in result.stderr.lower() or 'not signed in' in result.stdout.lower():
                return False
            return True
        except Exception as e:
            logging.error(f"Login status check error: {str(e)}")
            return False

    def is_connected(self):
        """VPN'in bağlı olup olmadığını kontrol eder."""
        try:
            result = subprocess.run(
                ['hotspotshield', 'status'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=10,  # 10 saniye timeout
                check=False
            )
            # Durum çıktısını kontrol et
            status_output = result.stdout.strip()
            logging.info(f"VPN Status Output: {status_output}")
            # Bağlantı durumunu kontrol et
            if "Connected" in status_output:
                return True
            elif "Not connected" in status_output:
                return False
            else:
                # Beklenmeyen bir çıktı varsa logla
                logging.warning(f"Unexpected status output: {status_output}")
                return False
        except Exception as e:
            logging.error(f"Connection status check error: {str(e)}")
            return False

    def update_status_display(self):
        """Durum ekranını ve düğmeleri günceller."""
        try:
            is_connected = self.is_connected()
            # Log kaydı ekle
            logging.info(f"Connection status: {'Connected' if is_connected else 'Not Connected'}")
            if is_connected:
                status_text = f'<span foreground="green">{self.lang.get_text("connected")}</span>'
                self.connect_button.set_sensitive(False)
                self.disconnect_button.set_sensitive(True)
            else:
                status_text = f'<span foreground="red">{self.lang.get_text("not_connected")}</span>'
                self.connect_button.set_sensitive(True)
                self.disconnect_button.set_sensitive(False)
            self.status_label.set_markup(status_text)
            # Tray menüsünü güncelle
            GLib.idle_add(lambda: self.indicator.set_menu(self.build_tray_menu()))
        except Exception as e:
            logging.error(f"Status display update error: {str(e)}")

    def show_notification(self, title, message):
        """Sistem bildirimi gösterir."""
        try:
            if not Notify.is_initted():
                Notify.init("Hotspot Shield VPN")
            notification = Notify.Notification.new(title, message, "network-vpn")
            notification.show()
        except Exception as e:
            logging.error(f"Notification error: {str(e)}")

    def show_error_message(self, title, message):
        """Hata mesajı iletişim kutusu gösterir."""
        try:
            dialog = Gtk.MessageDialog(
                parent=self.window,
                flags=0,
                message_type=Gtk.MessageType.ERROR,
                buttons=Gtk.ButtonsType.OK,
                text=title
            )
            dialog.format_secondary_text(message)
            dialog.run()
            dialog.destroy()
        except Exception as e:
            logging.error(f"Error message display error: {str(e)}")

    def quit(self, _):
        """Uygulamadan çıkar."""
        try:
            if self.is_connected():
                self.disconnect_vpn()
            if Notify.is_initted():
                Notify.uninit()
            Gtk.main_quit()
        except Exception as e:
            logging.error(f"Quit error: {str(e)}")
            Gtk.main_quit()

def main():
    """Ana fonksiyon, uygulamayı başlatır."""
    try:
        logging.info("Starting application...")
        app = HotspotShieldApp()
        app.window.show_all()
        Gtk.main()
    except Exception as e:
        logging.error(f"Application start error: {str(e)}")
        raise

if __name__ == "__main__":
    main()
