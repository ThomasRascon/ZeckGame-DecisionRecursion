FROM python

WORKDIR /usr/src/app

RUN pip install pysimplegui
RUN pip install numpy

COPY . .

CMD g++ -shared -o clibrary.so -fPIC -std=c++17 GraphStructure.cpp ZeckGame.cpp; python GraphColoring.py