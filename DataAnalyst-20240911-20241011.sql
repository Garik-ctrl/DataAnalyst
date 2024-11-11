-- vytáhnutí všech měst, které mají méně než 500.000, nebo více  než 9.900.000 obyvatel (včetně)
SELECT *
FROM city
Where Population >= 9900000 OR Population <= 500000
ORDER BY Population DESC

/* vytáhnutí všech měst,  které mají méně než 500.000, nebo více  než 9.900.000 obyvatel (včetně),
a zároveň nemají v názvu `District` "TAL" */
SELECT *
FROM city
Where `District` not like '%TAL%' and (Population >= 9900000 OR Population <= 5000)
ORDER BY Population DESC

/* vytáhnutí TOP 3 měst dle populace */
Select *
From city
Order by `Population` DESC
LIMIT 3

--vytvoření nového sloupečku na základě podmínky CASE
Select *,
CASE 
    WHEN `Population`>200000 and `CountryCode` like '%A%' THEN 'splneno' 
    WHEN `Population`>100000 and `CountryCode` like '%A%' THEN 'splneno2' 
    ELSE  'nesplneno'
END as 'splneno/nesplneno'
From city
Order by `Population` DESC
LIMIT 30

/*seznam okresů, které mají populaci menší než 20.000, nebo větší než 20.000.000 
a zobrazení průměrného množství obyvatel v okrese na město */
Select 
    DISTrict, 
    SUM(Population) as 'Suma populace',
    AVG(`Population`) as 'prumer'
From city
Group by `District`
HAVING SUM(Population)>20000000 OR SUM(Population)<20000
Order by Sum(`Population`) DESC, AVG(`Population`) DESC

/*zobrazení průměrného zastoupení jazyku zaokrouhleno na 2 desetinná místa */
Select 
    LANGUAGE
    ,ROUND(AVG(percentage),2) as 'průměr'
FROM countrylanguage
GROUP BY `Language`

/* propojení tabulek city, country a countrylanguage, zobrazení jednotlivých měst a oficiálního jazyku */
SELECT
    A.ID
    ,A.Name
    ,A.countryCode
    ,A.DIStrict
    ,A.population
    ,B.LifeExpectancy
    ,C.LANGUAGE
FROM city A 
LEFT JOIN country B ON A.CountryCode=B.Code
LEFT JOIN countrylanguage C ON A.`CountryCode`=C.`CountryCode`
WHERE C.`IsOfficial`='T'
Order by `Population` DESC



/* zobrazení District, průměrnou populaci, lifeEpectancy, LANGUAGE - pouze oficiální
- vidět výsledky, které mají průměrnou populaci nižší než 100000 */
SELECT
    A.DIStrict
    ,AVG(A.population)
    ,B.LifeExpectancy
    ,C.LANGUAGE
    ,C.`IsOfficial`
FROM city A 
LEFT JOIN country B ON A.CountryCode=B.Code
LEFT JOIN countrylanguage C ON A.`CountryCode`=C.`CountryCode`
WHERE C.`IsOfficial`='T'
GROUP BY
    A.DIStrict
    ,B.LifeExpectancy
    ,C.LANGUAGE
    ,C.`IsOfficial`
Order by AVG(A.population) DESC

-- vytvoření tabulky - musí obsahovat primary key 
Create Table KNIHY (
    ISBN VARCHAR(13) PRIMARY KEY,
    Title VARCHAR(255) NOT null,
    Author VARCHAR(255)	NOT null,
    Year INT not null,
    Genre VARCHAR(255)	NOT NULL,
    PageCount INT not null
)

-- příklad modifikování tabulky a jeho data typu
ALTER Table knihy
MODIFY ISBN VARCHAR(14)

-- příklad vložení dat do tabulky
INSERT INTO knihy (ISBN, Title, Author, YearOfPublication, Genre, PageCount) 
VALUES 
('978-0451524935', '1984', 'George Orwell', 1949, 'Dystopian Fiction', 328),
('978-0743273565', 'The Great Gatsby', 'F. Scott Fitzgerald', 1925, 'Classic Fiction', 180)
;

--výběr z nově vytvoření tabulky - všechny knihy vydané po roce 1900
SELECT *
From knihy
Where Year>1900

--výběr z nově vytvoření tabulky - počet knih pro daný žánr
SELECT 
    Genre
    ,count(*) as 'Pocet knih'
From knihy
Group BY
    Genre 
Order by count(*) DESC

--TOP 5 knih s nejvíce stránkami
select *
From knihy
Order by PageCount DESC
limit 5

--jednoduché propojení tabulek s podmínkou, že teplota je větší než 0
Select 
    A.*
    ,B.*
FROM cities A JOIN weather B ON A.`CityID`=B.`CityID`
Where B.`Temperature`>0

-- vytvoření tabulky dle zadání live coding
CREATE TABLE IF NOT EXISTS Cities (
    CityID INTEGER PRIMARY KEY,
    CityName VARCHAR(100),
    Country VARCHAR(100),
    Population INTEGER
);

-- naplnění daty
INSERT INTO Cities (CityID, CityName, Country, Population) VALUES
(1, 'New York', 'USA', 8419000),
(2, 'Los Angeles', 'USA', 3980400),
(3, 'Chicago', 'USA', 2706000),
(4, 'Houston', 'USA', 2325500),
(5, 'Phoenix', 'USA', 1680800),
(6, 'Philadelphia', 'USA', 1584200),
(7, 'San Antonio', 'USA', 1541200),
(8, 'San Diego', 'USA', 1423800),
(9, 'Dallas', 'USA', 1347900),
(10, 'San Jose', 'USA', 1026900),
(11, 'London', 'UK', 8982000),
(12, 'Birmingham', 'UK', 1141810),
(13, 'Leeds', 'UK', 789194),
(14, 'Glasgow', 'UK', 626410),
(15, 'Sheffield', 'UK', 584853),
(16, 'Bradford', 'UK', 536986),
(17, 'Liverpool', 'UK', 496784),
(18, 'Edinburgh', 'UK', 482005),
(19, 'Manchester', 'UK', 547627),
(20, 'Bristol', 'UK', 467099);

-- updatování dat v tabulce
UPDATE cities
SET `Country`="UK"
Where `Country`="Slovakia"


-- vytvoření návazných dat tzv kaskádovité propojení -> vidíme foreign key
CREATE TABLE IF NOT EXISTS Weather (
    WeatherID INTEGER PRIMARY KEY,
    CityID INTEGER,
    Date DATE,
    Temperature DECIMAL(5,2),
    Precipitation DECIMAL(5,2),
    FOREIGN KEY (CityID) REFERENCES Cities (CityID)
);

--naplnění dat
INSERT INTO Weather (WeatherID, CityID, Date, Temperature, Precipitation) VALUES
(1, 1, '2023-01-01', 5.5, 12.3),
(2, 2, '2023-01-02', 13.9, 5.1),
(3, 3, '2023-01-03', -1.1, 0.0),
(4, 4, '2023-01-04', 8.2, 25.4),
(5, 5, '2023-01-05', 21.1, 0.0),
(6, 6, '2023-01-06', 2.8, 1.2),
(7, 7, '2023-01-07', 14.4, 0.0),
(8, 8, '2023-01-08', 17.6, 0.0),
(9, 9, '2023-01-09', 9.0, 10.2),
(10, 10, '2023-01-10', 18.3, 0.0),
(11, 11, '2023-01-11', 7.2, 2.3),
(12, 12, '2023-01-12', 4.6, 12.0),
(13, 13, '2023-01-13', 3.3, 8.5),
(14, 14, '2023-01-14', 0.0, 15.6),
(15, 15, '2023-01-15', -2.2, 1.0),
(16, 16, '2023-01-16', 10.5, 0.0),
(17, 17, '2023-01-17', 12.7, 0.0),
(18, 18, '2023-01-18', 5.5, 0.0),
(19, 19, '2023-01-19', 8.8, 0.0),
(20, 20, '2023-01-20', 6.1, 5.0);


-- vložní dat do 'parent' tabulky Cities
INSERT INTO Cities (CityID, CityName, Country, Population) VALUES
(99, 'GARIK', 'USA', 8419000)

-- návazné vložní dat do 'child' tabulky Weather (naopak by to nefungovalo)
INSERT INTO Weather (WeatherID, CityID, Date, Temperature, Precipitation) VALUES
(99, 99, '2023-01-01', 100, 100)

-- smazání  řádku v tabulce 'child' tabulce
DELETE FROM Weather
WHERE CityID = 99;

-- smazání  řádku v tabulce 'parent' tabulce
DELETE FROM Cities
WHERE CityID = 99;


-- vytvoření view
Create View Pocasi AS 
Select 
    A.`CityName`
    ,SUM(B.`Precipitation`) as 'celkove srážky'
    ,ROUND(AVG(B.`Temperature`),2) as 'průměrná teplota'
FROM cities A JOIN weather B on A.`CityID`=B.`CityID`
Group BY
    A.`CityName`


--název města, okres, název země
Create VIEW Mesta AS(
SELECT
    A.ID
    ,A.Name AS "Název města"
    ,A.countryCode
    ,B.`Name` as "Stát"
    ,B. `Region`
    ,A.`District`
FROM city A 
LEFT JOIN country B ON A.CountryCode=B.Code)

--vymazání view
DROP view Mesta;


From city A left JOIN Jazyk B on A.`CountryCode`=B.
INSERT INTO Cities (CityID, CityName, Country, Population) VALUES
(99, 'GARIK', 'USA', 8419000)