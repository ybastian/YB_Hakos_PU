DROP TRIGGER "main"."trg_u_system_parameters";
DROP TRIGGER "main"."trg_d_system_parameters";
DROP TRIGGER "main"."trg_i_system_parameters";


CREATE TRIGGER trg_i_system_parameters AFTER INSERT ON system_parameters
BEGIN
    INSERT INTO system_parameters_history(parameter, value, history_reason, history_timestamp)
    VALUES(NEW.parameter, NEW.value, 'I', CURRENT_TIMESTAMP);		
END;

CREATE TRIGGER trg_u_system_parameters AFTER UPDATE ON system_parameters
BEGIN
    INSERT INTO system_parameters_history(parameter, value, history_reason, history_timestamp)
    VALUES(OLD.parameter, OLD.value, 'U', CURRENT_TIMESTAMP);		
END;

CREATE TRIGGER trg_d_system_parameters AFTER DELETE ON system_parameters
BEGIN
    INSERT INTO system_parameters_history(parameter, value, history_reason, history_timestamp)
    VALUES(OLD.parameter, OLD.value, 'D', CURRENT_TIMESTAMP);		
END;