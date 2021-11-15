DROP PROCEDURE IF EXISTS createHomeOwner


DELIMITER $$
CREATE PROCEDURE createHomeOwner ()
BEGIN
	DECLARE not_found INTEGER DEFAULT 0;
	DECLARE _finance_id INTEGER DEFAULT 0;
	DECLARE _home_id INTEGER DEFAULT 0;
	DECLARE _user_id INTEGER DEFAULT 0;
    DECLARE _home_owner_id INTEGER DEFAULT 0;
    DECLARE _exist_home_owner_id INTEGER DEFAULT 0;
	DECLARE _command_number varchar(15) DEFAULT "";
	DECLARE _person_id varchar(13) DEFAULT "";
	DECLARE _command_id varchar(15) DEFAULT "";
    DECLARE _is_stay INTEGER DEFAULT 0;
    

	DEClARE cur_finance_personid 
		CURSOR FOR SELECT finance_id, person_id, command, is_stay FROM finance_person WHERE home_owner IS NULL;
	-- declare NOT FOUND handler
	DECLARE CONTINUE HANDLER 
        FOR NOT FOUND SET not_found = 1;

	OPEN cur_finance_personid;
	SELECT Max(id) + 1 into _home_owner_id FROM Home_homeowner;
	
	importHomeOwner: LOOP
		set not_found = 0;
		FETCH cur_finance_personid INTO _finance_id, _person_id, _command_number, _is_stay;
		IF not_found = 1 THEN             
			LEAVE importHomeOwner;
		END IF;

        SELECT id into _home_id FROM Home_homedata WHERE finance_id = _finance_id;
        SELECT id into _user_id FROM UserData_user WHERE PersonID = _person_id;
		-- กรณีจับคู่บ้าน + คน ไม่ได้ ไม่บันทึก
        IF  not_found = 1 THEN
			ITERATE  importHomeOwner;
		END  IF;

		select id INTO _exist_home_owner_id FROM Home_homeowner WHERE home_id = _home_id AND owner_id = _user_id LIMIT 1;
		-- มีข้อมูลอยู่แล้ว ไม่ต้องบันทึก
		IF not_found = 1 THEN
			UPDATE finance_person SET home_owner = _exist_home_owner_id WHERE finance_id = _finance_id;
			ITERATE  importHomeOwner;
		END IF;
		set not_found = 0;
		-- กรณีจับคู่บ้าน + คน ได้ หาคำสั่ง ถ้ามีก็เอามาใส่ด้วย
		SELECT id into _command_id FROM Command_command WHERE CONCAT(number,"/",year) = _command_number;


		IF not_found = 0 THEN
			IF _is_stay = 1 THEN
				INSERT INTO Home_homeowner (id, is_stay, home_id, owner_id, leave_type, enter_command_id) VALUES (_home_owner_id, _is_stay, _home_id, _user_id, "-", _command_id);
			ELSEIF _is_stay = 0 THEN
				INSERT INTO Home_homeowner (id, is_stay, home_id, owner_id, leave_type, leave_command_id) VALUES (_home_owner_id, _is_stay, _home_id, _user_id, "-", _command_id);
			END IF;
		ELSE
			INSERT INTO Home_homeowner (id, is_stay, home_id, owner_id, leave_type) VALUES (_home_owner_id, _is_stay, _home_id, _user_id, "-");
		END IF;
		SET _home_owner_id = _home_owner_id + 1;
		-- select _home_id, _user_id, _command_id;


	END LOOP importHomeOwner;
	CLOSE cur_finance_personid;

END$$
DELIMITER ;

CALL createHomeOwner();

DROP PROCEDURE IF EXISTS set_home_owner_id_rent


DELIMITER $$
CREATE PROCEDURE set_home_owner_id_rent()
BEGIN
	DECLARE not_found INTEGER DEFAULT 0;
	DECLARE _return_vlue INTEGER DEFAULT 0;
	DECLARE _rent_id INTEGER DEFAULT 0;
	DECLARE _montly_bill INTEGER DEFAULT 0;
	DECLARE _user_id INTEGER DEFAULT 0;
	DECLARE _home_owner_id INTEGER DEFAULT 0;
	DECLARE _person_id varchar(13) DEFAULT "";
	DECLARE _is_stay INTEGER DEFAULT 0;
    

	DEClARE cur_rent_payment 
		CURSOR FOR SELECT id, PersonID, montly_bill FROM Payment_rentpayment WHERE home_owner_id is NULL;
	-- declare NOT FOUND handler
	DECLARE CONTINUE HANDLER 
        FOR NOT FOUND SET not_found = 1;

	OPEN cur_rent_payment;

	SetHomeOwnerID: LOOP
		set not_found = 0;
		FETCH cur_rent_payment INTO _rent_id, _person_id, _montly_bill;

		IF LENGTH(_person_id) < 13 THEN
			ITERATE SetHomeOwnerID;
		END IF;
		IF not_found = 1 THEN             
			LEAVE SetHomeOwnerID;
		END IF;


		-- กรณีจับคู่บ้าน + คน ไม่ได้ ไม่บันทึก
		SELECT id into _user_id FROM UserData_user WHERE PersonID = _person_id LIMIT 1;
        IF  not_found = 1 THEN
			UPDATE Payment_rentpayment SET comment = CONCAT("Not Found User if for PID = ",_person_id) WHERE id = _rent_id;
			INSERT INTO UserData_user (username, PersonID) VALUES (_person_id, _person_id);
			ITERATE SetHomeOwnerID;
		END IF;

		SELECT count(id) into _return_vlue FROM  Home_homeowner WHERE owner_id  = _user_id AND is_stay = 1 GROUP BY owner_id;
		IF _return_vlue <> 1 THEN
			ITERATE SetHomeOwnerID;
		END IF;

		SELECT id into _home_owner_id FROM Home_homeowner WHERE owner_id  = _user_id AND is_stay = 1 LIMIT 1;
		-- กรณีจับคู่บ้าน + คน ไม่ได้ ไม่บันทึก
        IF not_found = 1 THEN
			UPDATE Payment_rentpayment SET comment = CONCAT("Not Found _home_owner_id if for stay and _user_id = ",_user_id) WHERE id = _rent_id;
			ITERATE SetHomeOwnerID;
		END IF;

		UPDATE Payment_rentpayment SET home_owner_id = _home_owner_id WHERE id = _rent_id;
		-- select _home_id, _user_id, _command_id;

	END LOOP SetHomeOwnerID;
	CLOSE cur_rent_payment;

END$$
DELIMITER ;


DELIMITER $$

CREATE TRIGGER contacts_before_insert
BEFORE INSERT
   ON contacts FOR EACH ROW
BEGIN
   DECLARE vUser varchar(50);
   -- Find username of person performing INSERT into table
   SELECT USER() INTO vUser;
   -- Update create_date field to current system date
   SET NEW.created_date = SYSDATE();
   -- Update created_by field to the username of the person performing the INSERT
   SET NEW.created_by = vUser;
END; $$

DELIMITER ;

SET @sql = NULL;
SELECT
  GROUP_CONCAT(DISTINCT
    CONCAT(
      'SUM(CASE when date_format(date, \'%m-%d\') = ''',
      date_format(date, '%m-%d'),
      ''' then montly_bill end) AS ',
      date_format(date, '%m-%y'), ''
    )
  ) INTO @sql
FROM 
	Payment_rentpayment 
WHERE  
	date  >= DATE_SUB(NOW(),INTERVAL 13 MONTH)
ORDER BY 
	date asc;

SET @sql = CONCAT('CREATE TEMPORARY TABLE pivot_rent_payment SELECT home_owner_id , ', @sql, ' FROM Payment_rentpayment WHERE home_owner_id IS NOT NULL GROUP BY home_owner_id');

PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;



-- ปรับค่า Status ของบ้านที่มีคนพักให้เป็น ST

UPDATE home_homedata 
SET 
	status = 'ST' 
WHERE 
	id in (
			SELECT home_id 
			FROM home_homeowner 
			WHERE is_stay
		);

-- ปรับค่า Status ของบ้านที่เพิ่งย้ายออกให้เป็น WC (รอตรวจสอบ)

UPDATE home_homedata 
SET 
	status = 'WC' 
WHERE 
	status = 'ST'
		and
	id not in (
			SELECT home_id 
			FROM home_homeowner 
			WHERE is_stay
		);

