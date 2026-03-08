package it.uniroma3.siw.film.controllers.components.validators;

import org.springframework.validation.Errors;
import org.springframework.validation.Validator;

import it.uniroma3.siw.film.model.Attore;

import org.springframework.stereotype.Component;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;

@Slf4j
@Component
@RequiredArgsConstructor
public class AttoreValidator implements Validator {

    @Override
    public void validate(Object target, Errors errors) {
        log.info("Validazione Attore Iniziata");
        log.info("Validazione Attore Terminata");
    }
    
    @Override
    public boolean supports(Class<?> clazz) {
        return Attore.class.equals(clazz);
    }
}
