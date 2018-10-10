# MySQL Native Client in Python - Techacademy.az

MySQL Client/Server protokolunu daha yaxşı başa düşmək üçün python dilində sadə native mysql client. Təhsil məqsədlidir

### Prerequisites

Python3, pip, virtualenv

### Quraşdırılma

1. Repo-nu local kompüterimizə clone edirik:
```
git clone https://github.com/elshadaghazade/techacademy_mysql_native_client_in_python.git
```
2. Daha sonra fayllar olan qovluğa keçərək virtualenv-i set edirik:
```
cd techacademy_mysql_native_client_in_python
virtualenv -p $(which python3) .py3
```

3. Virtualenv set olduqdan sonra onu aktiv edirik:
```
source .py3/bin/activate
```

4. Asılıqları package.txt faylından yükləyirik:
```
pip install -r package.txt
```

7. client.py faylını run edirik:
```
python client.py
```

Qeyd: virtualenv-i deaktiv etmək üçün deactivate əmrini yazmağınız kifayətdir

### Python MySQL Native Client Testing
[![Python MySQL Native Client Testing](https://img.youtube.com/vi/lO81kjtdTYc/0.jpg)](https://www.youtube.com/watch?v=lO81kjtdTYc)

## Authors

* **Elshad Agayev** - *Fullstack Developer* - [LinkedIn Profile](https://www.linkedin.com/in/elshadaghazadeh/)
