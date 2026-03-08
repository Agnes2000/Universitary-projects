package it.uniroma3.siw.film.controllers.components.validators;

import org.springframework.stereotype.Component;
import org.springframework.validation.Errors;
import org.springframework.validation.Validator;

import it.uniroma3.siw.film.model.Credenziali;
import it.uniroma3.siw.film.services.CredenzialiService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;

@Slf4j
@Component
@RequiredArgsConstructor
public class CredenzialiValidator implements Validator {

    private final CredenzialiService credenzialiService;

    @Override
    public void validate(Object target, Errors errors) {
        log.info("Validazione Credenziali Iniziata");
        Credenziali credenziali = (Credenziali)target;
        String username = credenziali.getUsername().trim();
        String password = credenziali.getPassword().trim();

        log.debug("Validazione campo username");
        if(this.credenzialiService.esistonoCredenziali(username)) {
            log.debug("Username già utilizzato");
            errors.rejectValue("username", "Unique");
        }
        
        log.debug("Validazione campo password");
        if(password.length() < 6 || password.length() > 20) {
            log.debug("Campo password non rispetta lunghezza");
            errors.rejectValue("password", "Size");
        }
        
        log.info("Validazione Credenziali Terminata");
    }

    @Override
    public boolean supports(Class<?> clazz) {
        return Credenziali.class.equals(clazz);
    }

    
}
