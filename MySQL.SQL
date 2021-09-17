DROP PROCEDURE IF EXISTS `createHomeOwner`


DELIMITER $$
CREATE PROCEDURE createHomeOwner ()
BEGIN
	DECLARE not_found INTEGER DEFAULT 0;
	DECLARE _finance_id INTEGER DEFAULT 0;
	DECLARE _home_id INTEGER DEFAULT 0;
	DECLARE _user_id INTEGER DEFAULT 0;
    DECLARE _home_owner_id INTEGER DEFAULT 0;
	DECLARE _command_number varchar(15) DEFAULT "";
	DECLARE _person_id varchar(13) DEFAULT "";
	DECLARE _command_id varchar(15) DEFAULT "";
    DECLARE _is_stay INTEGER DEFAULT 0;
    

	DEClARE cur_finance_personid 
		CURSOR FOR SELECT finance_id, person_id, command, is_stay FROM finance_person;
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

		-- กรณีจับคู่บ้าน + คน ได้ หาคำสั่ง ถ้ามีก็เอามาใส่ด้วย
		SELECT id into _command_id FROM Command_command WHERE CONCAT(number,"/",year) = _command_number;

		select _home_owner_id, _is_stay, _home_id, _user_id;

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

CALL `createHomeOwner`();