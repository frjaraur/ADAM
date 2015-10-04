CREATE TABLE adam.credentials_type (
	id INT NOT NULL AUTO_INCREMENT,
	type char(25) NOT NULL,
    description char(250),
    PRIMARY KEY (id)
    );
    
CREATE TABLE adam.credentials (
	id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    salt char(250) NOT NULL,
    username char(250) NOT NULL,
    domain char(250),
    authfile MEDIUMBLOB,
    description char(250),
    credentials_type_id INT NOT NULL
    );    

ALTER TABLE credentials
ADD CONSTRAINT fk_credential_type
FOREIGN KEY (credentials_type_id) REFERENCES credentials_type (id)
ON DELETE CASCADE
ON UPDATE RESTRICT;
