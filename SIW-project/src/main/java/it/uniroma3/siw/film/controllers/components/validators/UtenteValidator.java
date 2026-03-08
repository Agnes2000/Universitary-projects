package it.uniroma3.siw.film.controllers.components.validators;

import org.springframework.stereotype.Component;
import org.springframework.validation.Errors;
import org.springframework.validation.Validator;

import it.uniroma3.siw.film.model.Utente;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;

@Slf4j
@Component
@RequiredArgsConstructor
public class UtenteValidator implements Validator {

    @Override
    public void validate(Object target, Errors errors) {
        log.info("Validazione Utente Iniziata");
        log.info("Validazione Utente Terminata");
    }

    @Override
    public boolean supports(Class<?> clazz) {
        return Utente.class.equals(clazz);
    }
    
}
