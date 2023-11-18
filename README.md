DBMS Project

CREATE DATABASE sports_booking;
use sports_booking;
CREATE TABLE sports (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL
);

CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(255) NOT NULL,
    password VARCHAR(255) NOT NULL,  -- Hashed in production
    email VARCHAR(255) NOT NULL,
    phone_number VARCHAR(15),
    roll_number VARCHAR(50) UNIQUE
);
CREATE TABLE slots (
    id INT AUTO_INCREMENT PRIMARY KEY,
    sport_id INT,
    slot_type ENUM('TueThuSat', 'MonWedFri') NOT NULL,
    time TIME NOT NULL,
    FOREIGN KEY (sport_id) REFERENCES sports(id)
);
CREATE TABLE bookings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    slot_id INT,
    booking_time DATETIME NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (slot_id) REFERENCES slots(id)
);
INSERT INTO sports (name) VALUES ('Badminton'), ('Basketball'), ('Yoga'), ('Gym'), ('Dance'), ('Table Tennis'), ('Martial Arts'), ('Chess');

INSERT INTO users (username, password, email, phone_number, roll_number) VALUES
('ishaan', 'password123', 'ish@example.com', '1234567890', 'RN1001');

INSERT INTO users (username, password, email, phone_number, roll_number) VALUES
('naman', 'password123', 'nam@example.com', '1234567890', 'RN1002');

INSERT INTO users (username, password, email, phone_number, roll_number) VALUES
('rishik', 'password123', 'nam@example.com', '1234567890', 'RN1003');

ALTER TABLE slots
ADD COLUMN end_time TIME NOT NULL AFTER time;
ALTER TABLE slots RENAME COLUMN time TO start_time; 

INSERT INTO slots (sport_id, slot_type, start_time, end_time) VALUES
(1, 'TueThuSat', '08:00:00', '09:00:00'),
(2, 'MonWedFri', '10:00:00', '11:00:00');

INSERT INTO slots (sport_id, slot_type, start_time, end_time) VALUES
(3, 'TueThuSat', '07:00:00', '09:00:00'),
(3, 'MonWedFri', '19:00:00', '11:00:00');

ALTER TABLE slots ADD COLUMN capacity INT NOT NULL;

select * from users;

DELIMITER //

CREATE TRIGGER check_slot_capacity BEFORE INSERT ON bookings
FOR EACH ROW
BEGIN
    DECLARE slot_capacity INT;
    DECLARE current_bookings INT;

    -- Get the capacity of the slot being booked
    SELECT capacity INTO slot_capacity FROM slots WHERE id = NEW.slot_id;

    -- Get the current number of bookings for the slot
    SELECT COUNT(*) INTO current_bookings FROM bookings WHERE slot_id = NEW.slot_id;

    -- Check if the capacity has been reached
    IF current_bookings >= slot_capacity THEN
        -- Prevent insertion and return an error
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Slot capacity exceeded';
    END IF;
END //

DELIMITER ;


UPDATE slots SET capacity = 12 WHERE id = 1;
UPDATE slots SET capacity = 15 WHERE id = 2;
UPDATE slots SET capacity = 10 WHERE id = 3;
UPDATE slots SET capacity = 20 WHERE id = 4;
