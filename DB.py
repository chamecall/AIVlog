import pymysql

class DB:
    def __init__(self, hostname, user_name, password, db_name):
        self.hostname = hostname
        self.user_name = user_name
        self.password = password
        self.db_name = db_name
        self.con = pymysql.connect(hostname, user_name, password, cursorclass=pymysql.cursors.DictCursor)

        self.cursor = self.con.cursor()
        self.create_db(db_name)

    def exec_query(self, query: str):
        self.cursor.execute(query)
        return self.cursor

    def exec_many_queries(self, template, data):
        self.cursor.executemany(template, data)

    def commit(self):
        self.con.commit()

    def rollback(self):
        self.con.rollback()

    def exec_template_query(self, template, values: tuple):
        self.cursor.execute(template, values)


    def create_db(self, db_name):

        self.exec_query('SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;')
        self.exec_query('SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;')
        self.exec_query("SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='TRADITIONAL,ALLOW_INVALID_DATES';")
        self.exec_query(f"CREATE SCHEMA IF NOT EXISTS `{db_name}` DEFAULT CHARACTER SET utf8 ;")
        self.exec_query(f'USE `{db_name}` ;')
        self.exec_query(f'''CREATE TABLE IF NOT EXISTS `Detections` (
                  `detection_id` INT(11) NOT NULL,
                  `frame_num` INT(10) UNSIGNED NOT NULL,
                  `dnn_label` VARCHAR(64) NULL DEFAULT NULL,
                  `box` VARCHAR(32) NULL DEFAULT NULL,
                  PRIMARY KEY (`detection_id`, `frame_num`))
                ENGINE = InnoDB
                DEFAULT CHARACTER SET = utf8;''')
        self.exec_query(f'''CREATE TABLE IF NOT EXISTS `Labels` (
                  `label_id` INT(11) NOT NULL,
                  `name` VARCHAR(64) NOT NULL,
                  PRIMARY KEY (`label_id`),
                  UNIQUE INDEX `name_UNIQUE` (`name` ASC))
                ENGINE = InnoDB
                DEFAULT CHARACTER SET = utf8;''')

        self.exec_query(f'''CREATE TABLE IF NOT EXISTS `Assignments` (
                  `frame_num` INT(11) UNSIGNED NOT NULL,
                  `label_id` INT(11) NULL DEFAULT NULL,
                  `detection_id` INT(11) NULL DEFAULT NULL,
                  INDEX `asdf_idx` (`label_id` ASC),
                  INDEX `detection_id_idx` (`detection_id` ASC),
                  CONSTRAINT `detection_id`
                    FOREIGN KEY (`detection_id`)
                    REFERENCES `{db_name}`.`Detections` (`detection_id`)
                    ON DELETE NO ACTION
                    ON UPDATE NO ACTION,
                  CONSTRAINT `label_id`
                    FOREIGN KEY (`label_id`)
                    REFERENCES `{db_name}`.`Labels` (`label_id`)
                    ON DELETE NO ACTION
                    ON UPDATE NO ACTION)
                ENGINE = InnoDB
                DEFAULT CHARACTER SET = utf8;''')

        self.exec_query(f'''CREATE TABLE IF NOT EXISTS `Media` (
              `media_id` INT(11) NOT NULL,
              `file_name` VARCHAR(255) NOT NULL,
              `type` ENUM('I', 'V', 'A', 'T') NOT NULL,
              `duration` INT UNSIGNED NOT NULL DEFAULT 0,
              PRIMARY KEY (`media_id`))
                ENGINE = InnoDB
            DEFAULT CHARACTER SET = utf8;''')

        self.exec_query(f'''CREATE TABLE IF NOT EXISTS `CommandType` (
              `command_type_id` INT(11) NOT NULL,
              `name` VARCHAR(128) NOT NULL,
              PRIMARY KEY (`command_type_id`))
            ENGINE = InnoDB
            DEFAULT CHARACTER SET = utf8;''')


        self.exec_query(f'''CREATE TABLE IF NOT EXISTS `Command` (
              `command_id` INT(11) NOT NULL,
                `name` VARCHAR(128) NOT NULL,
              `type` VARCHAR(128) NOT NULL,
              `trigger_event_id` INT NOT NULL,
              `attached_character_class` INT NOT NULL,
              `relation_class` INT NOT NULL,
              `command_type_id` INT NOT NULL,
              `media_id` INT NOT NULL,
              `duration` INT NOT NULL,
              PRIMARY KEY (`command_id`),
              INDEX `fk_Command_1_idx` (`media_id` ASC),
              INDEX `fk_Command_2_idx` (`command_type_id` ASC),
              INDEX `fk_Command_3_idx` (`attached_character_class` ASC),
              INDEX `fk_Command_4_idx` (`relation_class` ASC),
              CONSTRAINT `fk_Command_1`
                FOREIGN KEY (`media_id`)
                REFERENCES `{db_name}`.`Media` (`media_id`)
                ON DELETE NO ACTION
                ON UPDATE NO ACTION,
              CONSTRAINT `fk_Command_2`
                FOREIGN KEY (`command_type_id`)
                REFERENCES `{db_name}`.`CommandType` (`command_type_id`)
                ON DELETE NO ACTION
                ON UPDATE NO ACTION,
              CONSTRAINT `fk_Command_3`
                FOREIGN KEY (`attached_character_class`)
                REFERENCES `{db_name}`.`Labels` (`label_id`)
                ON DELETE NO ACTION
                ON UPDATE NO ACTION,
              CONSTRAINT `fk_Command_4`
                FOREIGN KEY (`relation_class`)
                REFERENCES `{db_name}`.`Labels` (`label_id`)
                ON DELETE NO ACTION
                ON UPDATE NO ACTION)
            ENGINE = InnoDB
            DEFAULT CHARACTER SET = utf8;''')

        self.exec_query('SET SQL_MODE=@OLD_SQL_MODE;')
        self.exec_query('SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;')
        self.exec_query('SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;')
        self.commit()
