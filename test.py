import pyautogui                # библилиотека для работы с окнами
import numpy as np                # библилиотека для работы с массивами
import cv2                # библилиотека компьютерного зрения
import threading                # библилиотека для работы с потоками
import sounddevice as sd                # библилиотека звукозаписи
import queue                # библилиотека для работы с очередями
import soundfile as sf                # библилиотека для чтения и записи звуковых файлов
from moviepy.editor import AudioFileClip, VideoFileClip                # библилиотека для редактирования видео
import tkinter as tk                # библилиотека ткинтера
from tkinter import messagebox                # библилиотека инфо окошка
import time                # библилиотека таймера


class ScreenRecorderApp:                # объявление класса скринрекордер
    def __init__(self, root):                # метод инициализации
        self.root = root                # запись рута в свойство класса
        self.root.title("Screen Recorder")                # заголовок окна приложения
        self.start_button = tk.Button(root, text="Start Recording", command=self.start_recording)                # создание кнопки старта записи
        self.start_button.pack()                # размещение стартовой кнопки
        self.stop_button = tk.Button(root, text="Stop Recording", command=self.stop_recording, state=tk.DISABLED)                # создание кнопки стоп
        self.stop_button.pack()                # размещение кнопки стоп

        self.screen_width, self.screen_height = pyautogui.size()   # установка размеров экрана

        self.fourcc = cv2.VideoWriter_fourcc(*"XVID")                # установка кодека
        self.out = None                # создание пустого объекта VideoWriter
        # Установка аудио параметров
        self.sample_rate = 44100  # качество CD
        self.audio_buffer = queue.Queue()                # создание объекта - очередь
        # установка флага состояния записи
        self.recording = False
        self.recording_thread = None

    def start_recording(self):                # метод начала записи
        self.recording = True                # флаг состояния записи меняется на противоположный
        self.out = cv2.VideoWriter("output_screen_recording.avi", self.fourcc, 20.0,
                                   (self.screen_width, self.screen_height))                # инициализация объекта VideoWriter и передача конструктуру параметров, описанных выше
        self.start_button.config(state=tk.DISABLED)                # кнопку СТАРТ tk формы делаем неюзабельной
        self.stop_button.config(state=tk.NORMAL)                # кнопку СТОП делаем юзабельной
        # Начало записывния видео в отдельный поток
        self.start_time = time.time()  # записывание стартового времени
        self.num_frames = 0  # инициализация счётчика кадров
        self.recording_thread = threading.Thread(target=self.record_screen)                # создание записывающего потока
        self.recording_thread.start()                # начало потока записи
        # Начало записи аудио
        with sd.InputStream(callback=self.record_audio, channels=2, samplerate=self.sample_rate):                #
            self.root.wait_window()  # Ожидание окончания записи

    def stop_recording(self):                # метод конца записи
        self.recording = False                # флаг состояния записи меняется на противоположный
        self.recording_thread.join()                # блокатор других потоков до тех пор пока не завершится этот поток
        self.out.release()                # делает объект класса VideoWriter снова пустым
        self.save_audio()                # вызов метода сохранения аудио
        self.combine_audio_video()                # вызов метода соединения аудио и видео
        self.start_button.config(state=tk.NORMAL)                # кнопку СТАРТ делаем юзабельной
        self.stop_button.config(state=tk.DISABLED)                # кнопку СТОП делаем неюзабельной
        messagebox.showinfo("Recording Finished", "Recording has been saved.") # выводим сообщение в информационном окне

    def record_screen(self):                # метод записи экрана
        while self.recording:                # пока флаг состояния записи True
            screenshot = pyautogui.screenshot()                # делаем скриншот
            frame = np.array(screenshot)                # добавляем скриншот в массив
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)                # делаем кадр цветным
            self.out.write(frame)                # записываем кадр в VideoWriter
            self.num_frames += 1  # Инкрементируем счётчик кадров

    def record_audio(self, indata, frames, time, status):                # метод записи звука
        self.audio_buffer.put(indata.copy())                #

    def save_audio(self):                # метод сохранения аудио
        audio_data = []                # инициализация
        while not self.audio_buffer.empty():                # пока аудио буффер не пустой
            audio_data.append(self.audio_buffer.get())                # добавление в конец массива элемента очереди
        audio_data = np.concatenate(audio_data, axis=0)                # объединение данных
        sf.write("output_recorded_audio.wav", audio_data, self.sample_rate)              # запись данных в звуковой файл

    def combine_audio_video(self):                # метод соединения аудио и видео
        video_clip = VideoFileClip("output_screen_recording.avi")                # привязка переменной к видеофайлу
        audio_clip = AudioFileClip("output_recorded_audio.wav")                # привязка переменной к аудиофайлу

        # рассчёт фактической частоты кадров на основе записанных кадров и затраченного времени
        actual_frame_rate = self.num_frames / (time.time() - self.start_time)

        final_clip = video_clip.set_audio(audio_clip)                # привязка к видео клипу аудио запись
        final_clip = final_clip.set_duration(audio_clip.duration)  # регуляция продолжительности итогового файла по файлу аудио записи
        final_clip = final_clip.set_fps(actual_frame_rate)  # установка фактической рассчитанной частоты кадров
        final_clip.write_videofile("output_video.mp4", codec="libx264")                # запись итогового клипа в новый файл


root = tk.Tk()                # создание главного окна приложения
app = ScreenRecorderApp(root)                # создание объекта класса скринкастера
root.mainloop()                # запуск цикла обработки событий