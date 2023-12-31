import mysql.connector
import sqlite3
from dateutil.parser import parse
conn = sqlite3.connect("lab7.db")
    
def fr1():
    new = conn.cursor()
    new.execute("""
    SELECT r.RoomCode,r.RoomName,r.beds,r.bedType,r.maxOcc,r.basePrice,r.decor,PopScore,date(checkout,'+1 days'), cast(julianday(checkout) - julianday(checkin) as integer),checkout
    FROM lab7_reservations l1
    join lab7_rooms r on l1.Room = r.RoomCode
    join (
        SELECT Room, ROUND(SUM(julianday(checkout) - julianday(checkin))/180,2) as PopScore
        FROM lab7_reservations
        WHERE julianday('now') - julianday(Checkout) < 180 
        AND julianday('now') - julianday(checkin)
        GROUP BY Room
        ORDER BY PopScore
    ) as l2 on l2.Room = l1.Room
    group by l1.Room 
    having max(checkout)
    order by PopScore;
    """)
    
    return new.fetchall()

def fr2():
    first = input("Please enter guest's first name: ").strip()
    last = input("Please enter guest's last name: ").strip()
    checkin = input("Please enter a valid check-in date (yyyy/mm/dd): ").strip()
    try:
        parse(checkin)
    except Exception: #invalid date format
        raise Exception("Invalid date format")
    checkout = input("Please enter a valid check-out date (yyyy/mm/dd): ").strip()
    try:
        parse(checkout)
    except Exception: #invalid date format
        raise Exception("Invalid date format")
    if checkin >= checkout:
        raise(Exception("Enter valid checkin/checkout dates. Returning to menu."))
    roomCode = input("Please enter a room code: ").strip()
    bedType = input("Please enter bed type (King,Queen,Double): ").strip()
    adults = input("Please enter number of adults: ")
    try:
        if int(adults) > 4:
            raise(Exception())
    except Exception:
        print("Invalid number of occupants")
        
    try:
        adults = int(adults)
    except:
        print("Invalid number")
    child = input("Please enter number of children: ")
    try:
        child = int(child)
    except:
        print("Invalid number")
    if len(roomCode) > 0:
        if len(bedType) > 0:
            query = """
            SELECT RoomCode, RoomName, beds, BedType, MaxOcc, BasePrice, decor 
            FROM lab7_rooms 
            WHERE (RoomCode = ?) AND (BedType = ?) AND
            MaxOcc >= ? AND RoomCode NOT IN (
                SELECT Room FROM lab7_reservations 
                WHERE (CheckIn BETWEEN ? AND ?) OR (Checkout BETWEEN ? AND ?))
                ORDER BY BasePrice ASC LIMIT 5""" 
            params =  (roomCode, bedType, adults + child, checkin, checkout, checkin, checkout)
        else:
            query = """
            SELECT RoomCode, RoomName, beds, BedType, MaxOcc, BasePrice, decor 
            FROM lab7_rooms 
            WHERE (RoomCode = ?) AND
            MaxOcc >= ? AND RoomCode NOT IN (
                SELECT Room FROM lab7_reservations 
                WHERE (CheckIn BETWEEN ? AND ?) OR (Checkout BETWEEN ? AND ?))
                ORDER BY BasePrice ASC LIMIT 5""" 
            params = (roomCode, adults + child, checkin, checkout, checkin, checkout)
    else:
        query = """
        SELECT RoomCode, RoomName, beds, BedType, MaxOcc, BasePrice, decor 
        FROM lab7_rooms 
        WHERE MaxOcc >= ? AND RoomCode NOT IN (
            SELECT Room FROM lab7_reservations 
            WHERE (CheckIn BETWEEN ? AND ?) OR (Checkout BETWEEN ? AND ?))
            ORDER BY BasePrice ASC LIMIT 5""" 
        params = (adults + child, checkin, checkout, checkin, checkout)
    new = conn.cursor()
    new.execute(query, params)
    res = new.fetchall()
    if res is None or res == []:
        res = similar(adults,child,checkin,checkout)
    return res,first,last,checkin,checkout,adults,child

def book(res,room):
    new = conn.cursor()
    query = "select max(code) from lab7_reservations"
    new.execute(query)
    code = new.fetchall()[0][0] + 1
    new.close()
    new = conn.cursor()
    query = "INSERT INTO lab7_reservations VALUES (?, ?, ?, ?, ?, ?, ?, ? ,?)"
    new.execute(query,[code,room[0],res[2],res[3],room[5],res[1],res[0],res[4],res[5]])
    print("Successfully Booked. Reservation number: "+str(code))
    return


def similar(adults,child,checkin,checkout):
    query = """
        SELECT RoomCode, RoomName, beds, BedType, MaxOcc, BasePrice, decor 
        FROM lab7_rooms 
        WHERE MaxOcc >= ? AND RoomCode NOT IN (
            SELECT Room FROM lab7_reservations 
            WHERE (CheckIn BETWEEN ? AND ?) OR (Checkout BETWEEN ? AND ?))
            ORDER BY BasePrice ASC LIMIT 5""" 
    params = (adults + child, checkin, checkout, checkin, checkout)
    new = conn.cursor()
    new.execute(query, params)
    return new.fetchall()


def fr3(code):#done
    try:
        new = conn.cursor()
        query = "delete from lab7_reservations where Code = " + code + ";"
        new.execute(query)
        print("Reservation",code,"has been deleted or did not exist.")
    except Exception as e:
        if e:
            print(e)
        print("Failed to delete reservation",code)
    finally:
        return

def fr4(): #done
    first = input("Please enter guest's first name: ").split()
    if len(first) == 0:
        first = ""
    else:
        first = first[0]
    last = input("Please enter guest's last name: ").split()
    if len(last) == 0:
        last = ""
    else:
        last = last[0]
    checkin = input("Please enter a valid check-in date (yyyy/mm/dd): ").split()
    if len(checkin) == 0:
        checkin = ""
    else:
        checkin = checkin[0]
        try:
            parse(checkin)
        except Exception: #invalid date format
            raise Exception("Invalid date format")
    checkout = input("Please enter a valid check-out date (yyyy/mm/dd): ").split()
    if len(checkout) == 0:
        checkout = ""
    else:
        checkout = checkout[0]
        try:
            parse(checkout)
        except Exception: #invalid date format
            raise Exception("Invalid date format")
    roomCode = input("Please enter a room code: ").split()
    if len(roomCode)  == 0:
        roomCode = ""
    else:
        roomCode = roomCode[0]
    reservationCode = input("Please enter a reservation code: ").split()
    if len(reservationCode )== 0:
        reservationCode = ""
    else:
        reservationCode = reservationCode[0]
    new = conn.cursor()
    query = "select code,room,roomName,checkin,checkout, rate,lastname,firstname,adults,kids from lab7_reservations join lab7_rooms on RoomCode = Room where Room like '%"+roomCode+"' and Code like'%"+reservationCode+"' and firstName like '%"+first+"' and lastName like '%"+last+"'"
    if checkin != "":
        if checkout != "":
            query+=" and checkin = '"+checkin+"' and checkout = '"+checkout+"'"
        else:
            query +=" and checkin = '"+checkin
    new.execute(query)
    return new.fetchall()

def fr5():#done
    new = conn.cursor()
    query = """
        SELECT Room,
        SUM(CASE
        WHEN STRFTIME('%m', checkin) = STRFTIME('%m', checkout) and STRFTIME('%m', checkout) = '01' THEN JULIANDAY(checkout) - JULIANDAY(checkin)
        WHEN STRFTIME('%m', checkout) = '01' AND STRFTIME('%m', checkin) != STRFTIME('%m', checkout) THEN JULIANDAY(checkout) - JULIANDAY(DATE(checkout, 'start of month'))
        WHEN STRFTIME('%m', checkin) = '01' AND STRFTIME('%m', checkout) != STRFTIME('%m', checkin) THEN JULIANDAY(DATE(checkin, 'start of month', '+1 month', '-1 day')) - JULIANDAY(checkin)
        ELSE 0
    END)*Rate as Jan,
    SUM(CASE
            WHEN STRFTIME('%m', checkin) = STRFTIME('%m', checkout) and STRFTIME('%m', checkout) = '02' THEN JULIANDAY(checkout) - JULIANDAY(checkin)
            WHEN STRFTIME('%m', checkout) = '02' AND STRFTIME('%m', checkin) != STRFTIME('%m', checkout) THEN JULIANDAY(checkout) - JULIANDAY(DATE(checkout, 'start of month'))
            WHEN STRFTIME('%m', checkin) = '02' AND STRFTIME('%m', checkout) != STRFTIME('%m', checkin) THEN JULIANDAY(DATE(checkin, 'start of month', '+1 month', '-1 day')) - JULIANDAY(checkin)
            ELSE 0
    END)*Rate as Feb,
    SUM(CASE
        WHEN STRFTIME('%m', checkin) = STRFTIME('%m', checkout) and STRFTIME('%m', checkout) = '03' THEN JULIANDAY(checkout) - JULIANDAY(checkin)
        WHEN STRFTIME('%m', checkout) = '03' AND STRFTIME('%m', checkin) != STRFTIME('%m', checkout) THEN JULIANDAY(checkout) - JULIANDAY(DATE(checkout, 'start of month'))
        WHEN STRFTIME('%m', checkin) = '03' AND STRFTIME('%m', checkout) != STRFTIME('%m', checkin) THEN JULIANDAY(DATE(checkin, 'start of month', '+1 month', '-1 day')) - JULIANDAY(checkin)
        ELSE 0
    END)*Rate as Mar,
    SUM(CASE
            WHEN STRFTIME('%m', checkin) = STRFTIME('%m', checkout) and STRFTIME('%m', checkout) = '04' THEN JULIANDAY(checkout) - JULIANDAY(checkin)
            WHEN STRFTIME('%m', checkout) = '04' AND STRFTIME('%m', checkin) != STRFTIME('%m', checkout) THEN JULIANDAY(checkout) - JULIANDAY(DATE(checkout, 'start of month'))
            WHEN STRFTIME('%m', checkin) = '04' AND STRFTIME('%m', checkout) != STRFTIME('%m', checkin) THEN JULIANDAY(DATE(checkin, 'start of month', '+1 month', '-1 day')) - JULIANDAY(checkin)
            ELSE 0
    END)*Rate as Apr,
    SUM(CASE
        WHEN STRFTIME('%m', checkin) = STRFTIME('%m', checkout) and STRFTIME('%m', checkout) = '05' THEN JULIANDAY(checkout) - JULIANDAY(checkin)
        WHEN STRFTIME('%m', checkout) = '05' AND STRFTIME('%m', checkin) != STRFTIME('%m', checkout) THEN JULIANDAY(checkout) - JULIANDAY(DATE(checkout, 'start of month'))
        WHEN STRFTIME('%m', checkin) = '05' AND STRFTIME('%m', checkout) != STRFTIME('%m', checkin) THEN JULIANDAY(DATE(checkin, 'start of month', '+1 month', '-1 day')) - JULIANDAY(checkin)
        ELSE 0
    END)*Rate as May,
    SUM(CASE
            WHEN STRFTIME('%m', checkin) = STRFTIME('%m', checkout) and STRFTIME('%m', checkout) = '06' THEN JULIANDAY(checkout) - JULIANDAY(checkin)
            WHEN STRFTIME('%m', checkout) = '06' AND STRFTIME('%m', checkin) != STRFTIME('%m', checkout) THEN JULIANDAY(checkout) - JULIANDAY(DATE(checkout, 'start of month'))
            WHEN STRFTIME('%m', checkin) = '06' AND STRFTIME('%m', checkout) != STRFTIME('%m', checkin) THEN JULIANDAY(DATE(checkin, 'start of month', '+1 month', '-1 day')) - JULIANDAY(checkin)
            ELSE 0
    END)*Rate as Jun,
    SUM(CASE
        WHEN STRFTIME('%m', checkin) = STRFTIME('%m', checkout) and STRFTIME('%m', checkout) = '07' THEN JULIANDAY(checkout) - JULIANDAY(checkin)
        WHEN STRFTIME('%m', checkout) = '07' AND STRFTIME('%m', checkin) != STRFTIME('%m', checkout) THEN JULIANDAY(checkout) - JULIANDAY(DATE(checkout, 'start of month'))
        WHEN STRFTIME('%m', checkin) = '07' AND STRFTIME('%m', checkout) != STRFTIME('%m', checkin) THEN JULIANDAY(DATE(checkin, 'start of month', '+1 month', '-1 day')) - JULIANDAY(checkin)
        ELSE 0
    END)*Rate as Jul,
    SUM(CASE
            WHEN STRFTIME('%m', checkin) = STRFTIME('%m', checkout) and STRFTIME('%m', checkout) = '08' THEN JULIANDAY(checkout) - JULIANDAY(checkin)
            WHEN STRFTIME('%m', checkout) = '08' AND STRFTIME('%m', checkin) != STRFTIME('%m', checkout) THEN JULIANDAY(checkout) - JULIANDAY(DATE(checkout, 'start of month'))
            WHEN STRFTIME('%m', checkin) = '08' AND STRFTIME('%m', checkout) != STRFTIME('%m', checkin) THEN JULIANDAY(DATE(checkin, 'start of month', '+1 month', '-1 day')) - JULIANDAY(checkin)
            ELSE 0
    END)*Rate as Aug,
    SUM(CASE
        WHEN STRFTIME('%m', checkin) = STRFTIME('%m', checkout) and STRFTIME('%m', checkout) = '09' THEN JULIANDAY(checkout) - JULIANDAY(checkin)
        WHEN STRFTIME('%m', checkout) = '09' AND STRFTIME('%m', checkin) != STRFTIME('%m', checkout) THEN JULIANDAY(checkout) - JULIANDAY(DATE(checkout, 'start of month'))
        WHEN STRFTIME('%m', checkin) = '09' AND STRFTIME('%m', checkout) != STRFTIME('%m', checkin) THEN JULIANDAY(DATE(checkin, 'start of month', '+1 month', '-1 day')) - JULIANDAY(checkin)
        ELSE 0
    END)*Rate as Sep,
    SUM(CASE
            WHEN STRFTIME('%m', checkin) = STRFTIME('%m', checkout) and STRFTIME('%m', checkout) = '10' THEN JULIANDAY(checkout) - JULIANDAY(checkin)
            WHEN STRFTIME('%m', checkout) = '10' AND STRFTIME('%m', checkin) != STRFTIME('%m', checkout) THEN JULIANDAY(checkout) - JULIANDAY(DATE(checkout, 'start of month'))
            WHEN STRFTIME('%m', checkin) = '10' AND STRFTIME('%m', checkout) != STRFTIME('%m', checkin) THEN JULIANDAY(DATE(checkin, 'start of month', '+1 month', '-1 day')) - JULIANDAY(checkin)
            ELSE 0
    END)*Rate as Oct,
    SUM(CASE
        WHEN STRFTIME('%m', checkin) = STRFTIME('%m', checkout) and STRFTIME('%m', checkout) = '11' THEN JULIANDAY(checkout) - JULIANDAY(checkin)
        WHEN STRFTIME('%m', checkout) = '11' AND STRFTIME('%m', checkin) != STRFTIME('%m', checkout) THEN JULIANDAY(checkout) - JULIANDAY(DATE(checkout, 'start of month'))
        WHEN STRFTIME('%m', checkin) = '11' AND STRFTIME('%m', checkout) != STRFTIME('%m', checkin) THEN JULIANDAY(DATE(checkin, 'start of month', '+1 month', '-1 day')) - JULIANDAY(checkin)
        ELSE 0
    END)*Rate as Nov,
    SUM(CASE
            WHEN STRFTIME('%m', checkin) = STRFTIME('%m', checkout) and STRFTIME('%m', checkout) = '12' THEN JULIANDAY(checkout) - JULIANDAY(checkin)
            WHEN STRFTIME('%m', checkout) = '12' AND STRFTIME('%m', checkin) != STRFTIME('%m', checkout) THEN JULIANDAY(checkout) - JULIANDAY(DATE(checkout, 'start of month'))
            WHEN STRFTIME('%m', checkin) = '12' AND STRFTIME('%m', checkout) != STRFTIME('%m', checkin) THEN JULIANDAY(DATE(checkin, 'start of month', '+1 month', '-1 day')) - JULIANDAY(checkin)
            ELSE 0
    END)*Rate as Dec,
    SUM((JULIANDAY(checkout) - JULIANDAY(checkin))*Rate) as Total
    FROM lab7_reservations
    GROUP BY Room;
    """
    new.execute(query)
    return new.fetchall()


def main():
    print("\nWelcome to Inn Reservation System.\n")

    while 1:
        inp = input("Select an option:\n 1: Rooms and Rates\n 2: Reservations\n 3: Reservation Cancellation\n 4: Search\n 5: Revenue\n>")
        if inp.lower() == 'exit':
            print("Exiting!")
            break
        try:
            inp_lst = inp.split()
            num = int(inp_lst[0])
            if num not in range(1,6):
                raise(Exception)
            print("\nOption %d selected!:" % num )
            match num:
                case 1:
                    res = fr1()
                    print("RoomCode, RoomName, Beds, bedType, maxOcc, basePrice, decor, Popularity Score, Next Avail. Checkin, Length of Most Recent Stay, Date of Most Recent Checkout")
                    for line in res:
                        print(*line,sep=", ")
                case 2:
                    res = fr2()
                    print("Room details for Reservation: ")
                    for i, line in enumerate(res[0], start=1):
                        print(f"{i}. {line}")
                    cont = input("Do you wish to book? (y/n): ")
                    if cont not in('y','n'):
                        raise(Exception("Error, please enter valid option. Returning to main menu."))
                    if cont == 'n':
                        continue
                    option = input("Select an option (number) from list of rooms to book: ")
                    try:
                        option = int(option)
                    except Exception:
                            print("Invalid option")
                    book(res[1:],res[0][int(option)-1])
                case 3:
                    code = input("Please enter a reservation to be deleted.\n>")
                    try:
                        code = int(code)
                        fr3(str(code))
                    except Exception:
                        print("Code incorrectly formatted")
                case 4:
                    res = fr4()
                    if res == []:
                        print("No results.")
                    else:
                        print("Search Results: ")
                        for line in res:
                            print(line)
                case 5:
                    res = fr5()
                    if res is None:
                        print("error")
                    else:
                        print("Revenue Totals per room:\nRoomCode, Jan, Feb, Mar, Apr, May, Jun, Jul, Aug, Sep, Oct, Nov, Dec, Total Annual")
                        for line in res:
                            print(*line,sep=", ")
                case default:
                    print("Num not recognized")
        except Exception as e:
            if e:
                print(e) # comment out in final
            print("Operation failed\n")

 # setup db and tables
def setup():
    # mysql to get reservations
    cnx = mysql.connector.connect(user='jkalsi', password='CSC365_F23_027775364', host='mysql.labthreesixfive.com', port=3306, database='INN')
    try:
        # create cursor
        c1 = cnx.cursor()
    except mysql.connector.Error as e:
        print('Connection error: ',e)
    c1.execute("""
        SELECT CODE, Room,
  DATE_ADD(CheckIn, INTERVAL 154 MONTH),
  DATE_ADD(Checkout, INTERVAL 154 MONTH),
  Rate, LastName, FirstName, Adults, Kids FROM reservations;
     """)
    res = c1.fetchall()
    c1.close()

    #sqlite3
    cursor = conn.cursor()
    try:
        cursor.execute("DROP TABLE IF EXISTS lab7_rooms")
        cursor.execute("""
    CREATE TABLE IF NOT EXISTS lab7_rooms (
    RoomCode char(5) PRIMARY KEY,
    RoomName varchar(30) NOT NULL,
    Beds int(11) NOT NULL,
    bedType varchar(8) NOT NULL,
    maxOcc int(11) NOT NULL,
    basePrice DECIMAL(6,2) NOT NULL,
    decor varchar(20) NOT NULL,
    UNIQUE (RoomName)
    );
    """)
        room_data = [
        ('AOB', 'Abscond or bolster', 2, 'Queen', 4, 175, 'traditional'),
        ('CAS', 'Convoke and sanguine', 2, 'King', 4, 175, 'traditional'),
        ('FNA', 'Frugal not apropos', 2, 'King', 4, 250, 'traditional'),
        ('HBB', 'Harbinger but bequest', 1, 'Queen', 2, 100, 'modern'),
        ('IBD', 'Immutable before decorum', 2, 'Queen', 4, 150, 'rustic'),
        ('IBS', 'Interim but salutary', 1, 'King', 2, 150, 'traditional'),
        ('MWC', 'Mendicant with cryptic', 2, 'Double', 4, 125, 'modern'),
        ('RND', 'Recluse and defiance', 1, 'King', 2, 150, 'modern'),
        ('RTE', 'Riddle to exculpate', 2, 'Queen', 4, 175, 'rustic'),
        ('TAA', 'Thrift and accolade', 1, 'Double', 2, 75, 'modern'),
    ]

        cursor.executemany('''
        INSERT INTO lab7_rooms (RoomCode, RoomName, Beds, bedType, maxOcc, basePrice, decor)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', room_data)
        cursor.execute("DROP TABLE IF EXISTS lab7_reservations")
        conn.execute("""
    CREATE TABLE IF NOT EXISTS lab7_reservations (
    CODE int(11) PRIMARY KEY,
    Room char(5) NOT NULL,
    CheckIn date NOT NULL,
    Checkout date NOT NULL,
    Rate DECIMAL(6,2) NOT NULL,
    LastName varchar(15) NOT NULL,
    FirstName varchar(15) NOT NULL,
    Adults int(11) NOT NULL,
    Kids int(11) NOT NULL,
    FOREIGN KEY (Room) REFERENCES lab7_rooms (RoomCode)
    );
    """)
        for line in res:
            cursor.executemany("INSERT INTO lab7_reservations VALUES (?, ?, ?, ?, ?, ?, ?, ? ,?)",[line])

        conn.commit()
    except Exception as e:
        print(e)
    cursor.close()

if __name__=="__main__":
    setup()
    main()

