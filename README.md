### Tạo OPENAI API KEY
Tạo file .env, nhập thông tin API vào file này.
```python
[openai]
OPENAI_API_KEY=your-api-key
```
### Cài đặt các thư viện
```python
pip install -r requirements.txt
```
### Chạy ứng dụng
```python
chainlit run app.py
```
### Lưu ý: Chạy lại data_builder.py khi có sách mới được thêm vào folder data/book_storage
Hiện tại custom data đang được lưu trong folder data/book_storage.
```python
python data_builder.py
```
