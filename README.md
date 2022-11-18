# EMCalculations

Проект, где хранятся модули, описывающие расчёты электрических машин для ИЦ «Русэлпром». Пока частично выполнен только расчёт турбомашин (то есть, двух- и четырёхполюсных синхронных генераторов), но работа ведётся. В окончательном варианте предполагается создание единой системы максимально унифицированных друг с другом модулей, позволяющей рассчитывать любую из стандартных машин переменного тока.

## Содержание проекта

Проект, на данный момент, сожержит два пакета модулей на Python 3.8:

* `common`: здесь хранятся модули, предполагаемые общими для всех типов машин. А именно, это расчёты статора и его обмоток, коллекции электротехнических сталей и стандартных проводников.

* `turbo`: модули, описывающие специфические детали расчёта турбомашин: обмотки ротора, потерь, магнитной цепи и т. д.

## Пояснения о стиле кода

Весь проект написан в ООП-стиле. Может возникнуть вопрос, а почему так, если вся программа делает мало что, помимо перемалывания чисел. В таком случае самым подходящим кажется процедурный стиль, как часто пишут на MATLAB. Ответ: процедурный код сложно использовать повторно. Другой вопрос: а почему тогда не функциональный стиль? Ответ: в описываемых в настоящем проекте расчётах очень часто используются разного рода коэффициенты и вспомогательные значения, получаемые также расчётом. При написании функциональным стилем пришлось бы каждый раз пересчитывать их, увечичивая вероятность ошибок в расчёте, а также время расчёта. Кроме того, Python обладает крайне скудными средствами функционального программирования.

Названия большинства методов во всех классах отражают суть выполняемой ими операции, чему я уделяю особое внимание. Кроме того, методы, чьи имена начинаются с `get` (например, `get_armature_coefficient` класса `ACMachineStator`) возвращают значение, ничего не записывая в атрибуты класса, а методы с названиями на `compute` (например, `compute_stator_armature_reactance` класса `Reactances`) наоборот, вычисляют значение атрибута класса, ничего не возвращая.

Все методы имеют полную сигнатуру типа, указывающую, сколько аргументов и какого типа он ожидает, и что возвращает. Кроме того, сигнатуру типа имеют также атрибуты класса, чей тип не ясен заранее (то есть те, которые вычисляются уже после создания экземпляра класса). Это совершенно не обязательно и никак не влияет на выполнение. Тем менее, я счёл, что так лучше, исходя из опыта знакомства с языком Haskell, где знание типа функции сильно упрощает жизнь.

Почти для всех классов определен атрибут `__slots__`. Это сделано из соображений экономии памяти, чтобы не хранить значительно больший в объёме `__dict__`. Также, почти все классы являются «одиночками», то есть не допускают создания двух экземпляров одновременно. Это сделано в качестве меры предосторожности от случайного перезаписывания объекта во время выполнения.
