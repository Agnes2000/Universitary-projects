package it.uniroma3.siw.film.controllers.components.validators;

import org.springframework.validation.Validator;

import org.springframework.stereotype.Component;
import org.springframework.validation.Errors;

import it.uniroma3.siw.film.model.Recensione;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;

@Slf4j
@Component
@RequiredArgsConstructor
public class RecensioneValidator implements Validator{

    @Override
    public void validate(Object target, Errors errors) {
        log.info("Validazione Recensione Iniziata");
        log.info("Validazione Recensione Terminata");
    }

    @Override
    public boolean supports(Class<?> clazz) {
        return Recensione.class.equals(clazz);
    }

}
